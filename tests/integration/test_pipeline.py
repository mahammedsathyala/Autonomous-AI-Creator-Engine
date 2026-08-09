import sys
import os
import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from aegis.database import Base
from aegis.agent.orchestrator import orchestrator

class TestIntegrationPipeline(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=self.engine)
        Session = sessionmaker(bind=self.engine)
        self.db = Session()

    def tearDown(self):
        self.db.close()

    def test_full_autonomous_software_pipeline(self):
        project = orchestrator.create_project(
            db=self.db,
            name="Integration Test API",
            description="Build a REST API with FastAPI and SQLite."
        )
        self.assertIsNotNone(project.id)

        res = orchestrator.run_autonomous_pipeline(self.db, project.id)
        self.assertEqual(res["status"], "COMPLETED")
        self.assertIn("app.py", res["written_files"])
        self.assertEqual(res["quality_gates"]["status"], "APPROVED")

if __name__ == "__main__":
    unittest.main()
