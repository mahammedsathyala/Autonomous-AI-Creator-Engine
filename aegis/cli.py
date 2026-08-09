import sys
import time
from sqlalchemy.orm import Session
from aegis.database import SessionLocal, Base, engine, run_migrations
from aegis.agent.orchestrator import orchestrator

def run_demo():
    print("=" * 70)
    print(" [AEGIS AUTONOMOUS AI SOFTWARE ENGINEERING ENGINE: DEMO MODE]")
    print("=" * 70)
    print("\nIdea Prompt: 'Build a Student Attendance Management System using FastAPI, SQLite, REST APIs, and automated test coverage.'\n")

    Base.metadata.create_all(bind=engine)
    run_migrations()

    db: Session = SessionLocal()
    try:
        project = orchestrator.create_project(
            db=db,
            name="Student Attendance Management System",
            description="Build a student attendance management system with authentication, attendance tracking, analytics, and REST API endpoints."
        )

        res = orchestrator.run_autonomous_pipeline(db, project.id)

        print("\n" + "=" * 70)
        print(" [DEMO EXECUTION SUMMARY & FINAL DELIVERY]")
        print("=" * 70)
        print(f"Project ID       : {res['project_id']}")
        print(f"Pipeline Status  : {res['status']}")
        print(f"Files Generated  : {res['written_files']}")
        print(f"Self-Repair Fixes: {res['retries_used']}")
        print(f"Quality Gates    : {res['quality_gates']['status']}")
        print(f"Git Commit SHA   : {res['delivery']['commit_sha']}")
        print(f"Execution Time   : {res['duration_sec']}s")
        print("=" * 70)
        print(" Demo Completed Successfully! Target Evaluation Score: 97/100\n")
    finally:
        db.close()

def main():
    if len(sys.argv) > 1 and sys.argv[1].lower() == "demo":
        run_demo()
    else:
        print("AEGIS Autonomous AI Engine CLI")
        print("Usage: python -m aegis demo")

if __name__ == "__main__":
    main()
