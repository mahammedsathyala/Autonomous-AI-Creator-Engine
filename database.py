import sqlite3
import json
import os
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

DB_FILE = os.path.join(os.path.dirname(__file__), "agent_storage.db")

def get_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Table for storing agent personas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agents (
            agent_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            domain TEXT NOT NULL,
            editorial_voice TEXT,
            rejection_standards TEXT,
            created_at TEXT NOT NULL
        )
    """)
    
    # Table for storing published posts
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id TEXT PRIMARY KEY,
            agent_id TEXT NOT NULL,
            created_at TEXT NOT NULL,
            text TEXT NOT NULL,
            rationale TEXT NOT NULL,
            sources TEXT NOT NULL,
            topic_title TEXT,
            FOREIGN KEY (agent_id) REFERENCES agents (agent_id)
        )
    """)
    
    # Table for editorial evaluations (Accepted & Rejected topics)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS topic_evaluations (
            id TEXT PRIMARY KEY,
            agent_id TEXT NOT NULL,
            topic_title TEXT NOT NULL,
            source_url TEXT,
            status TEXT NOT NULL, -- 'ACCEPTED' or 'REJECTED'
            score INTEGER NOT NULL,
            reason TEXT NOT NULL,
            evaluated_at TEXT NOT NULL
        )
    """)
    
    # Table for agent memory (topics, keywords, concepts previously published)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memory_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id TEXT NOT NULL,
            post_id TEXT NOT NULL,
            topic_key TEXT NOT NULL,
            summary TEXT NOT NULL,
            keywords TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()

def save_agent(agent_id: str, name: str, domain: str, editorial_voice: str = "", rejection_standards: str = ""):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    cursor.execute("""
        INSERT OR REPLACE INTO agents (agent_id, name, domain, editorial_voice, rejection_standards, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (agent_id, name, domain, editorial_voice, rejection_standards, now))
    conn.commit()
    conn.close()

def get_agent(agent_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM agents WHERE agent_id = ?", (agent_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def save_post(post_id: str, agent_id: str, text: str, rationale: str, sources: List[str], created_at: str, topic_title: str = ""):
    conn = get_db()
    cursor = conn.cursor()
    sources_json = json.dumps(sources)
    cursor.execute("""
        INSERT INTO posts (id, agent_id, created_at, text, rationale, sources, topic_title)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (post_id, agent_id, created_at, text, rationale, sources_json, topic_title))
    conn.commit()
    conn.close()

def get_posts(agent_id: str, limit: int = 100) -> List[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, created_at AS createdAt, text, rationale, sources, topic_title
        FROM posts
        WHERE agent_id = ?
        ORDER BY datetime(created_at) DESC
        LIMIT ?
    """, (agent_id, limit))
    rows = cursor.fetchall()
    conn.close()
    
    posts = []
    for row in rows:
        p = dict(row)
        try:
            p['sources'] = json.loads(p['sources'])
        except Exception:
            p['sources'] = []
        posts.append(p)
    return posts

def save_evaluation(eval_id: str, agent_id: str, topic_title: str, source_url: str, status: str, score: int, reason: str):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    cursor.execute("""
        INSERT INTO topic_evaluations (id, agent_id, topic_title, source_url, status, score, reason, evaluated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (eval_id, agent_id, topic_title, source_url, status, score, reason, now))
    conn.commit()
    conn.close()

def get_evaluations(agent_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, topic_title, source_url, status, score, reason, evaluated_at
        FROM topic_evaluations
        WHERE agent_id = ?
        ORDER BY datetime(evaluated_at) DESC
        LIMIT ?
    """, (agent_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def save_memory(agent_id: str, post_id: str, topic_key: str, summary: str, keywords: List[str]):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    keywords_str = ",".join(keywords)
    cursor.execute("""
        INSERT INTO memory_items (agent_id, post_id, topic_key, summary, keywords, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (agent_id, post_id, topic_key, summary, keywords_str, now))
    conn.commit()
    conn.close()

def get_memories(agent_id: str) -> List[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT post_id, topic_key, summary, keywords, created_at
        FROM memory_items
        WHERE agent_id = ?
        ORDER BY datetime(created_at) DESC
    """, (agent_id,))
    rows = cursor.fetchall()
    conn.close()
    
    memories = []
    for r in rows:
        item = dict(r)
        item['keywords'] = item['keywords'].split(",") if item['keywords'] else []
        memories.append(item)
    return memories

# Initialize DB structure on load
init_db()
