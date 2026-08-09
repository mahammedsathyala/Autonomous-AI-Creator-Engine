# AEGIS System Architecture & Technical Specifications

AEGIS is an autonomous AI software engineering platform operating under two distinct modes:

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

## Creator Mode Pipeline & State Machine

AEGIS enforces an explicit 17-state finite state machine:
`CREATED` → `REQUIREMENTS_ANALYZED` → `PLANNED` → `RESEARCHED` → `ARCHITECTED` → `IMPLEMENTING` → `BUILDING` → `TESTING` → `FAILED` → `REPAIRING` → `RETESTING` → `REVIEWING` → `SECURITY_REVIEW` → `VALIDATED` → `GIT_COMMIT` → `READY` → `COMPLETED`.

## 10 Specialized Agents

1. **RequirementAgent**: Analyzes scope, constraints, and acceptance criteria.
2. **PlannerAgent**: Builds milestone plan and task graph DAG.
3. **ResearchAgent**: Identifies tech stack, libraries, and security patterns.
4. **ArchitectAgent**: Designs schemas, folder layout, and OpenAPI contracts.
5. **CoderAgent**: Writes multi-file codebases in sandbox workspace.
6. **TestAgent**: Generates unit test suites and executes test runner.
7. **ReviewerAgent**: Evaluates code maintainability and architectural quality.
8. **RepairAgent**: Performs self-repair loop matching tracebacks to failure memory.
9. **SecurityAgent**: Scans for secrets, shell injection, and path traversal.
10. **DeliveryAgent**: Creates Git commits, release bundles, and deployment reports.
