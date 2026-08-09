import sys
import os
import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from aegis.database import Base
from aegis.agent.belief_engine import belief_engine
from aegis.models import BeliefModel

class TestBeliefEngine(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=self.engine)
        Session = sessionmaker(bind=self.engine)
        self.db = Session()
        self.agent_id = "test-agent-ada"

    def tearDown(self):
        self.db.close()

    def test_belief_creation(self):
        belief = belief_engine.record_or_update_belief(
            db=self.db,
            agent_id=self.agent_id,
            subject="CVE-2026-8812 KV Cache Exfiltration",
            statement="Model weights exfiltration possible via KV cache side channel.",
            evidence_type="FACT",
            confidence=0.85
        )
        self.assertIsNotNone(belief.id)
        self.assertEqual(belief.subject, "CVE-2026-8812 KV Cache Exfiltration")
        self.assertEqual(belief.evidence_type, "FACT")
        self.assertEqual(belief.confidence, 0.85)

    def test_supporting_evidence_confidence_update(self):
        b1 = belief_engine.record_or_update_belief(
            db=self.db,
            agent_id=self.agent_id,
            subject="Prompt Injection in RAG",
            statement="Indirect prompt injection affects agentic tool calling.",
            evidence_type="CLAIM",
            confidence=0.70,
            supporting_event="Confirmed by Schneier analysis"
        )
        initial_conf = b1.confidence

        b2 = belief_engine.record_or_update_belief(
            db=self.db,
            agent_id=self.agent_id,
            subject="Prompt Injection in RAG",
            statement="Indirect prompt injection affects agentic tool calling.",
            evidence_type="FACT",
            confidence=0.90,
            supporting_event="CVE advisory published"
        )
        self.assertGreater(b2.confidence, initial_conf)

    def test_contradictory_evidence(self):
        b1 = belief_engine.record_or_update_belief(
            db=self.db,
            agent_id=self.agent_id,
            subject="Product X Vulnerability",
            statement="Product X is affected by critical buffer overflow vulnerability.",
            evidence_type="CLAIM",
            confidence=0.80
        )

        b2 = belief_engine.record_or_update_belief(
            db=self.db,
            agent_id=self.agent_id,
            subject="Product X Vulnerability",
            statement="Vendor advisory states Product X is not affected.",
            evidence_type="FACT",
            confidence=0.95,
            contradicting_event="Vendor patch confirms false alarm"
        )

        self.assertEqual(b2.status, "CONTRADICTED")
        self.assertLess(b2.confidence, 0.80)

if __name__ == "__main__":
    unittest.main()
