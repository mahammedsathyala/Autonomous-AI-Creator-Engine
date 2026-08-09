# AEGIS — Autonomous AI Software Engineering Platform

> **An autonomous AI software creation and engineering engine that converts natural-language ideas into tested, reviewed, security-audited, self-repaired, version-controlled software artifacts inside a controlled sandbox.**

[![AEGIS CI Pipeline](https://github.com/mahammedsathyala/Autonomous-AI-Creator-Engine/actions/workflows/ci.yml/badge.svg)](https://github.com/mahammedsathyala/Autonomous-AI-Creator-Engine/actions)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Evaluation Target](https://img.shields.io/badge/Target-97%2F100-brightgreen.svg)](#)

---

## 🌟 Architectural Overview

AEGIS operates under two major modes:

```text
                                            +-----------------------------------+
                                            |               AEGIS               |
                                            +-----------------+-----------------+
                                                              |
                                      +-----------------------+-----------------------+
                                      |                                               |
                                      v                                               v
                        +---------------------------+                   +---------------------------+
                        |      RESEARCH MODE        |                   |       CREATOR MODE        |
                        | (Autonomous Tech Ingestion|                   | (Autonomous AI Software   |
                        | & 5-Dim Editorial Voice)  |                   |  Engineering Engine)      |
                        +---------------------------+                   +---------------------------+
```

---

## 🚀 17-State Finite State Machine (FSM)

`CREATED` → `REQUIREMENTS_ANALYZED` → `PLANNED` → `RESEARCHED` → `ARCHITECTED` → `IMPLEMENTING` → `BUILDING` → `TESTING` → `FAILED` → `REPAIRING` → `RETESTING` → `REVIEWING` → `SECURITY_REVIEW` → `VALIDATED` → `GIT_COMMIT` → `READY` → `COMPLETED`

---

## 🤖 10 Specialized Autonomous Agents

1. **RequirementAgent**: Analyzes natural language software ideas into explicit requirements, constraints, and success conditions.
2. **PlannerAgent**: Builds project milestones, task DAGs, and execution dependencies.
3. **ResearchAgent**: Researches technical patterns, dependencies, and API structures.
4. **ArchitectAgent**: Designs database schemas, OpenAPI contracts, and multi-file directory structures.
5. **CoderAgent**: Writes application source code inside isolated sandbox workspaces.
6. **TestAgent**: Generates unit test suites and executes runner capturing stdout/stderr.
7. **ReviewerAgent**: Inspects code maintainability, architecture quality, and performance.
8. **RepairAgent**: Self-repair loop matching failure tracebacks against Failure Memory.
9. **SecurityAgent**: Scans for secrets, shell injection vectors, and unsafe path traversal.
10. **DeliveryAgent**: Packages delivery bundles, generates documentation, and creates Git commits.

---

## ⚡ Deterministic Demo Mode CLI

Run the full end-to-end autonomous software creation loop locally:

```bash
python -m aegis demo
```

---

## 🔌 API Endpoints

### Autonomous Creator Mode API
- `POST /api/projects`: Create software project from natural-language prompt.
- `GET /api/projects`: List all software projects.
- `GET /api/projects/{id}`: Detailed project telemetry, tasks DAG, and state transitions.
- `POST /api/projects/{id}/run`: Execute autonomous multi-agent creation pipeline.
- `GET /api/metrics`: Platform observability (tokens, cost $, success rate %, repair rate %).
- `GET /api/approvals`: Human approval gate queue.
- `GET /api/memory`: Multi-layer memory explorer.

---

## 🛠️ Quickstart

### 1. Installation
```bash
git clone https://github.com/mahammedsathyala/Autonomous-AI-Creator-Engine.git
cd Autonomous-AI-Creator-Engine
pip install -r aegis/requirements.txt
```

### 2. Run Test Suite
```bash
python -m unittest discover -s tests -p "test_*.py"
python -m unittest discover -s tests/unit -p "test_*.py"
python -m unittest discover -s tests/integration -p "test_*.py"
```

### 3. Start AEGIS Operations Center Server
```bash
python app.py
```
Open **[http://localhost:8000](http://localhost:8000)** in your browser.

---

## 📜 License
MIT License - see [LICENSE](LICENSE) for details.
