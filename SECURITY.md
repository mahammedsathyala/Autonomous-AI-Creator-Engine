# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 2.0.x   | :white_check_mark: |
| 1.0.x   | :x:                |

## Security Architecture & Threat Model

AEGIS incorporates multi-layered security controls:
- **Sandbox Process Isolation**: AI-generated applications execute in isolated subprocesses/Docker containers with CPU, memory, and execution timeout bounds.
- **Security Agent Scan**: Scans all generated code for hardcoded secrets, shell injection vectors (`os.system`, `subprocess(shell=True)`), path traversal, and unsafe code execution before approval.
- **Controlled Tool Permissions**: Every tool invocation (`filesystem`, `terminal`, `git`) is authorized per agent and recorded in the audit log.
- **Human Approval Gates**: Intercepts high-risk operations (destructive deletion, remote git push, database drops) until approved by an administrator.

## Reporting a Vulnerability

Please report any security vulnerabilities directly to:
`mahamadhu036@gmail.com`
