import sys
import os
import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from aegis.database import Base
from aegis.agent.memory_system import memory_system

class TestMemorySystemUnit(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=self.engine)
        Session = sessionmaker(bind=self.engine)
        self.db = Session()
        self.project_id = "mem-prj-001"

    def tearDown(self):
        self.db.close()

    def test_failure_memory_recording_and_matching(self):
        stderr = "ModuleNotFoundError: No module named 'fastapi'"
        solution = "pip install fastapi uvicorn"
        
        memory_system.record_failure_solution(self.db, self.project_id, stderr, solution)
        found_sol = memory_system.find_failure_solution(self.db, stderr)
        
        self.assertEqual(found_sol, solution)

    def test_project_memory_save_and_retrieve(self):
        data = {"tech_stack": "FastAPI, SQLite, Python 3.13"}
        memory_system.save_project_memory(self.db, self.project_id, "tech_config", data)
        retrieved = memory_system.get_project_memory(self.db, self.project_id, "tech_config")
        
        self.assertEqual(retrieved, data)

if __name__ == "__main__":
    unittest.main()
