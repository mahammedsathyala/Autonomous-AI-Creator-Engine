# AEGIS REST API Specification

## Autonomous Creator Mode API

### 1. Create Project (`POST /api/projects`)
```json
{
  "name": "Student Attendance Management System",
  "description": "Build a student attendance tracking API with REST endpoints."
}
```

### 2. List Projects (`GET /api/projects`)

### 3. Get Project Details (`GET /api/projects/{id}`)

### 4. Execute Autonomous Pipeline (`POST /api/projects/{id}/run`)

### 5. Platform Metrics Telemetry (`GET /api/metrics`)

### 6. Human Approval Gates (`GET /api/approvals`, `POST /api/approvals/{id}/approve`)

### 7. Memory Explorer (`GET /api/memory`)

---

## Research Persona Mode API (Preserved Baseline)

### 1. Initialize Persona (`POST /api/agent/init`)

### 2. Retrieve Published Feed (`GET /api/agent/feed?agentId=...`)

### 3. Agent Telemetry (`GET /api/agent/status`)
