import sys
import os
import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from aegis.database import Base
from aegis.agent.agents import requirement_agent, planner_agent, architect_agent, reviewer_agent
from aegis.agent.security_agent import security_agent

class TestAgentsUnit(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=self.engine)
        Session = sessionmaker(bind=self.engine)
        self.db = Session()
        self.project_id = "test-prj-001"

    def tearDown(self):
        self.db.close()

    def test_requirement_agent(self):
        res = requirement_agent.run(self.db, self.project_id, "Build a Student Management System")
        self.assertEqual(res["status"], "SUCCESS")
        self.assertIn("requirements", res)

    def test_planner_agent(self):
        res = planner_agent.run(self.db, self.project_id, "Build a Student Management System")
        self.assertEqual(res["status"], "SUCCESS")
        self.assertIn("plan", res)

    def test_architect_agent(self):
        res = architect_agent.run(self.db, self.project_id, "Build a Student Management System")
        self.assertEqual(res["status"], "SUCCESS")
        self.assertIn("architecture", res)

    def test_reviewer_agent(self):
        res = reviewer_agent.run(self.db, self.project_id)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertGreaterEqual(res["review"]["score"], 90.0)

if __name__ == "__main__":
    unittest.main()
