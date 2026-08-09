import sys
import os
import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from aegis.database import Base
from aegis.agent.belief_engine import belief_engine
from aegis.models import BeliefModel, BeliefRelationshipModel, BeliefHistoryModel

class TestBeliefEngineP0(unittest.TestCase):
    def setUp(self):
        # In-memory SQLite DB for testing
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=self.engine)
        Session = sessionmaker(bind=self.engine)
        self.db = Session()
        self.agent_id = "test-agent-ada"

    def tearDown(self):
        self.db.close()

    def test_01_belief_creation(self):
        belief = belief_engine.record_or_update_belief(
            db=self.db,
            agent_id=self.agent_id,
            subject="CVE-2026-8812 KV Cache Exfiltration",
            statement="Model weights exfiltration possible via KV cache side channel.",
            evidence_type="FACT",
            confidence=0.85,
            source_url="https://cisa.gov/advisory/2026-8812"
        )
        self.assertIsNotNone(belief.id)
        self.assertEqual(belief.subject, "CVE-2026-8812 KV Cache Exfiltration")
        self.assertEqual(belief.evidence_type, "FACT")
        self.assertEqual(belief.confidence, 0.85)
        self.assertEqual(belief.status, "ACTIVE")

    def test_02_supporting_evidence_confidence_update(self):
        # Initial belief
        b1 = belief_engine.record_or_update_belief(
            db=self.db,
            agent_id=self.agent_id,
            subject="Prompt Injection in RAG",
            statement="Indirect prompt injection affects agentic tool calling.",
            evidence_type="CLAIM",
            confidence=0.70,
            source_url="https://darkreading.com/rag-injection"
        )
        initial_conf = b1.confidence

        # Independent supporting evidence
        b2 = belief_engine.record_or_update_belief(
            db=self.db,
            agent_id=self.agent_id,
            subject="Prompt Injection in RAG",
            statement="Indirect prompt injection affects agentic tool calling.",
            evidence_type="FACT",
            confidence=0.90,
            source_url="https://schneier.com/rag-analysis"
        )
        self.assertGreater(b2.confidence, initial_conf)

        # Verify history trail
        history = belief_engine.get_belief_history(self.db, b1.id)
        self.assertGreaterEqual(len(history), 2)
        self.assertEqual(history[0].previous_confidence, initial_conf)

    def test_03_contradictory_evidence_and_conflict(self):
        # Initial belief
        b1 = belief_engine.record_or_update_belief(
            db=self.db,
            agent_id=self.agent_id,
            subject="Product X Vulnerability",
            statement="Product X is affected by critical buffer overflow vulnerability.",
            evidence_type="CLAIM",
            confidence=0.80,
            source_url="https://thehackernews.com/product-x-vuln"
        )

        # Contradicting advisory
        b2 = belief_engine.record_or_update_belief(
            db=self.db,
            agent_id=self.agent_id,
            subject="Product X Vulnerability",
            statement="Vendor advisory states Product X is not affected.",
            evidence_type="FACT",
            confidence=0.95,
            source_url="https://vendor-x.com/security-response"
        )

        self.assertNotEqual(b1.id, b2.id)
        self.assertEqual(b1.status, "CONTRADICTED")
        self.assertLess(b1.confidence, 0.80)

        # Verify CONTRADICTS relationship
        rels = belief_engine.get_belief_relationships(self.db, b1.id)
        self.assertGreaterEqual(len(rels), 1)
        self.assertEqual(rels[0].relationship_type, "CONTRADICTS")

        # Verify conflict retrieval
        conflicts = belief_engine.get_conflicts(self.db, self.agent_id)
        self.assertGreaterEqual(len(conflicts), 1)

    def test_04_source_independence_penalty(self):
        # First source from darkreading.com
        b1 = belief_engine.record_or_update_belief(
            db=self.db,
            agent_id=self.agent_id,
            subject="Supply Chain Attack",
            statement="Malicious dependency identified in npm repository.",
            evidence_type="FACT",
            confidence=0.75,
            source_url="https://darkreading.com/npm-attack-1"
        )
        conf_after_1 = float(b1.confidence)

        # Second source from SAME domain darkreading.com (Syndicated repost)
        b2 = belief_engine.record_or_update_belief(
            db=self.db,
            agent_id=self.agent_id,
            subject="Supply Chain Attack",
            statement="Malicious dependency identified in npm repository.",
            evidence_type="FACT",
            confidence=0.75,
            source_url="https://darkreading.com/npm-attack-2"
        )
        conf_after_2 = float(b2.confidence)
        delta_same_domain = conf_after_2 - conf_after_1

        # Third source from NEW independent domain cisa.gov
        b3 = belief_engine.record_or_update_belief(
            db=self.db,
            agent_id=self.agent_id,
            subject="Supply Chain Attack",
            statement="Malicious dependency identified in npm repository.",
            evidence_type="FACT",
            confidence=0.75,
            source_url="https://cisa.gov/advisory-npm"
        )
        conf_after_3 = float(b3.confidence)
        delta_new_domain = conf_after_3 - conf_after_2

        # Independent domain boost should be significantly higher than same-domain boost
        self.assertGreater(delta_new_domain, delta_same_domain)

if __name__ == "__main__":
    unittest.main()
