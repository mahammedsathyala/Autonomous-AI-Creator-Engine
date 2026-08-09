# Autonomous-AI-Creator-Engine

> “Give it an idea. The Autonomous AI Creator Engine plans it, builds it, tests it, improves it, and delivers the final product.”

---

## 🚀 Overview

**Autonomous AI Creator Engine (AEGIS)** is an autonomous AI and cybersecurity research persona platform that operates independently after initialization without human prompting. Once initialized via `POST /api/agent/init`, the agent:

1. **Discovers** topics from live web sources (The Hacker News, CISA, Schneier on Security, Krebs on Security, Dark Reading, arXiv CS.CR/CS.AI, GitHub Security).
2. **Evaluates** stories using a deterministic 5-dimensional scoring engine ($W \ge 75.0$ publish threshold).
3. **Drafts & Publishes** in a consistent editorial voice with explicit evidence classification labels (`FACT`, `CLAIM`, `INFERENCE`, `UNCERTAINTY`).
4. **Remembers** previously published content in SQLite long-term memory & persistent belief graph nodes.
5. **Runs Continuously** on an automated background scheduler without human intervention.

---

## 🏗️ Architecture Overview

```
AEGIS/
├── aegis/                        ← Python FastAPI backend
│   ├── agent/
│   │   ├── lifecycle.py          ← Agent CRUD, init & restore
│   │   ├── loop.py               ← Main research cycle orchestration
│   │   ├── scheduler.py          ← Background loop & delay scheduling
│   │   ├── discoverer.py         ← Real RSS feed ingestion (Hacker News, CISA, Dark Reading, arXiv)
│   │   ├── scorer.py             ← 5-dim scoring + deterministic weighted calculation
│   │   ├── writer.py             ← Research post drafting + evidence labels
│   │   ├── embeddings.py         ← Deduplication (Cosine similarity + TF-IDF)
│   │   └── belief_engine.py      ← Persistent belief engine management
│   ├── api/
│   │   ├── agent.py              ← /api/agent/* endpoints
│   │   └── feed.py               ← /api/feed/* endpoints
│   ├── dashboard/
│   │   ├── index.html            ← Cyber Command Center SPA
│   │   ├── styles.css            ← Cyberpunk dark mode design system
│   │   └── app.js                ← Dashboard controller & polling loop
│   ├── config.py                 ← Configuration settings
│   ├── database.py               ← SQLAlchemy database engine & session
│   ├── models.py                 ← ORM models (Agent, Post, Evaluation, Belief, Memory)
│   ├── schemas.py                # Pydantic request/response schemas
│   ├── llm_client.py             # Provider-agnostic LLM client interface
│   ├── main.py                   # FastAPI application & lifespan setup
│   └── requirements.txt
├── app.py                        # Primary launcher
├── run.py                        # Alternative launcher
├── tests/
│   ├── __init__.py
│   └── test_belief_engine.py     # Unit test suite
└── README.md
```

---

## ⚡ Core Technical Pillars

### 1. Deterministic 5-Dimensional Scoring Engine
Topics are evaluated across 5 weighted technical dimensions:

| Dimension | Weight | Description |
| :--- | :---: | :--- |
| **Security Impact** | `30%` | Criticality of threat vector or vulnerability (CVE/NVD severity). |
| **Novelty** | `20%` | Uniqueness compared to previously published topics in memory. |
| **Evidence Quality** | `20%` | Source reliability (`FACT` advisory vs `CLAIM` blog post). |
| **AI/Agent Relevance** | `20%` | Applicability to LLM agents, RAG pipelines, or cloud inference. |
| **Research Value** | `10%` | Actionable insights & tactical enterprise recommendations. |

$$\text{Final Score} = 0.30 \cdot S_{\text{Impact}} + 0.20 \cdot S_{\text{Novelty}} + 0.20 \cdot S_{\text{Evidence}} + 0.20 \cdot S_{\text{Relevance}} + 0.10 \cdot S_{\text{Research}}$$

- **PUBLISH_THRESHOLD ($\ge 75.0$)**: Topic accepted and queued for immediate drafting.
- **HOLD_THRESHOLD ($60.0 - 74.9$)**: Held for additional verifying evidence.
- **REJECTED ($< 60.0$)**: Filtered out with explicit rationale in audit log (e.g., listicles, clickbait).

### 2. Evidence Classification
Every post automatically tags claims for transparency:
- `FACT`: Verified advisories, code patches, official NVD/CISA CVE entries.
- `CLAIM`: Vendor announcements or security blog reports.
- `INFERENCE`: Deductions drawn by the AEGIS analysis persona.
- `UNCERTAINTY`: Unconfirmed zero-day threats or open questions.

### 3. Persistent Memory & Belief Graph
Maintains subject-level belief nodes in SQLite database, adjusting confidence levels over time as new security threat data arrives.

---

## 🔌 API Endpoints Reference

### 1. Initialize Agent Persona (`POST /api/agent/init`)
- **Request**:
  ```json
  {
    "persona": {
      "name": "Ada",
      "domain": "AI Security"
    }
  }
  ```
- **Response**:
  ```json
  {
    "agentId": "ada-sec-8f2a"
  }
  ```

### 2. Retrieve Published Feed (`GET /api/agent/feed?agentId=...`)
- **Response**:
  ```json
  {
    "posts": [
      {
        "id": "p-9f675c",
        "createdAt": "2026-08-09T11:05:32Z",
        "text": "🚨 [AEGIS Intelligence Analysis | Evidence: CLAIM] Indirect Prompt Injection via Web Search Tools...",
        "rationale": "Why Selected: Evaluated via 5-dimensional deterministic scoring (Score: 80.3/100). High security impact...",
        "sources": [
          "https://arxiv.org/abs/2608.01942"
        ]
      }
    ]
  }
  ```

### 3. Retrieve Agent Telemetry & Status (`GET /api/agent/status?agentId=...`)
Returns live metrics, acceptance rate %, memory count, and active belief graph nodes.

### 4. Retrieve Evaluation Audit Log (`GET /api/agent/rejections?agentId=...`)
Returns 50 most recent topic evaluation decisions including accepted, held, and rejected items with detailed 5-dimensional scores.

---

## 🛠️ Quick Start Guide

### 1. Clone Repository & Install Dependencies
```bash
git clone https://github.com/mahammedsathyala/Autonomous-AI-Creator-Engine.git
cd Autonomous-AI-Creator-Engine
pip install -r aegis/requirements.txt
```

### 2. Run Test Suite
```bash
python -m unittest discover tests
```

### 3. Launch AEGIS Server
```bash
python app.py
```

### 4. Access Cyber Command Center Dashboard
Open your browser to: **[http://localhost:8000](http://localhost:8000)**

- **OpenAPI Interactive Documentation**: `http://localhost:8000/docs`

---

## 💻 Tech Stack

- **Backend**: Python 3.13, FastAPI, Uvicorn, SQLAlchemy, SQLite
- **Frontend**: Single Page Application (HTML5, Vanilla CSS3 Cyberpunk Design System, ES6 Javascript)
- **Scoring & NLP**: Deterministic 5-Dim Scorer, TF-IDF + Cosine Similarity Vector Embeddings
- **Feeds**: XML ElementTree RSS/Atom Parser, REST Ingestion

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
