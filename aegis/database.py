import os
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from aegis.config import settings

# Ensure data directory exists
data_dir = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(data_dir, exist_ok=True)

db_path = os.path.join(data_dir, "aegis.db")
engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def init_db():
    """Initializes all database tables and runs schema migrations."""
    Base.metadata.create_all(bind=engine)
    run_migrations()

def run_migrations():
    """Applies lightweight SQLite column/table migrations for upgraded schema."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check beliefs table
        cursor.execute("PRAGMA table_info(beliefs)")
        cols = [r[1] for r in cursor.fetchall()]
        if cols:
            if "status" not in cols:
                cursor.execute("ALTER TABLE beliefs ADD COLUMN status TEXT DEFAULT 'ACTIVE'")
            if "source_references" not in cols:
                cursor.execute("ALTER TABLE beliefs ADD COLUMN source_references TEXT DEFAULT '[]'")
            if "supporting_events" not in cols:
                cursor.execute("ALTER TABLE beliefs ADD COLUMN supporting_events TEXT DEFAULT '[]'")
            if "contradicting_events" not in cols:
                cursor.execute("ALTER TABLE beliefs ADD COLUMN contradicting_events TEXT DEFAULT '[]'")
            if "created_at" not in cols:
                cursor.execute("ALTER TABLE beliefs ADD COLUMN created_at TEXT")

        # Check metrics_summary table
        cursor.execute("PRAGMA table_info(metrics_summary)")
        m_cols = [r[1] for r in cursor.fetchall()]
        if m_cols:
            if "security_pass_rate" not in m_cols:
                cursor.execute("ALTER TABLE metrics_summary ADD COLUMN security_pass_rate FLOAT DEFAULT 100.0")

        # Check projects table
        cursor.execute("PRAGMA table_info(projects)")
        p_cols = [r[1] for r in cursor.fetchall()]
        if p_cols:
            if "quality_gate_passed" not in p_cols:
                cursor.execute("ALTER TABLE projects ADD COLUMN quality_gate_passed BOOLEAN DEFAULT 0")

        # Check tasks table
        cursor.execute("PRAGMA table_info(tasks)")
        t_cols = [r[1] for r in cursor.fetchall()]
        if t_cols:
            if "parent_task" not in t_cols:
                cursor.execute("ALTER TABLE tasks ADD COLUMN parent_task TEXT")
            if "dependencies" not in t_cols:
                cursor.execute("ALTER TABLE tasks ADD COLUMN dependencies TEXT DEFAULT '[]'")
            if "priority" not in t_cols:
                cursor.execute("ALTER TABLE tasks ADD COLUMN priority INTEGER DEFAULT 1")
            if "input_json" not in t_cols:
                cursor.execute("ALTER TABLE tasks ADD COLUMN input_json TEXT DEFAULT '{}'")
            if "output_json" not in t_cols:
                cursor.execute("ALTER TABLE tasks ADD COLUMN output_json TEXT DEFAULT '{}'")
            if "retry_count" not in t_cols:
                cursor.execute("ALTER TABLE tasks ADD COLUMN retry_count INTEGER DEFAULT 0")
            if "error_msg" not in t_cols:
                cursor.execute("ALTER TABLE tasks ADD COLUMN error_msg TEXT")
            if "created_at" not in t_cols:
                cursor.execute("ALTER TABLE tasks ADD COLUMN created_at TEXT")
            if "started_at" not in t_cols:
                cursor.execute("ALTER TABLE tasks ADD COLUMN started_at TEXT")
            if "completed_at" not in t_cols:
                cursor.execute("ALTER TABLE tasks ADD COLUMN completed_at TEXT")

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[Migration] Note during table check: {e}")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
