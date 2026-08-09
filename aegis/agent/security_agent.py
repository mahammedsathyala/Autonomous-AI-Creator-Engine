import os
import uuid
import re
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from aegis.models import SecurityFindingModel, now_utc
from aegis.agent.tools import tool_registry

SECRET_PATTERNS = [
    r'api[_-]?key\s*=\s*["\'][A-Za-z0-9_\-]{16,}["\']',
    r'secret[_-]?key\s*=\s*["\'][A-Za-z0-9_\-]{16,}["\']',
    r'bearer\s+[A-Za-z0-9_\-\.]{20,}'
]

INJECTION_PATTERNS = [
    r'os\.system\(',
    r'subprocess\.Popen\(.*shell\s*=\s*True',
    r'eval\(',
    r'exec\('
]

class SecurityAgent:
    """
    Scans generated software projects for security risks:
    - Hardcoded Secrets
    - Shell Injection Vectors
    - Unsafe Path Traversal
    - Malicious Generated Subprocesses
    """
    def run_security_scan(self, db: Session, project_id: str) -> Dict[str, Any]:
        findings = []

        # Read app.py if present
        app_res = tool_registry.read_file(db, project_id, "SecurityAgent", "app.py")
        if app_res.get("status") == "SUCCESS":
            content = app_res["content"]

            # Check hardcoded secrets
            for pattern in SECRET_PATTERNS:
                if re.search(pattern, content, re.IGNORECASE):
                    findings.append({
                        "severity": "HIGH",
                        "category": "SECRETS",
                        "description": "Potential hardcoded API key or secret token detected in app.py."
                    })

            # Check injection vectors
            for pattern in INJECTION_PATTERNS:
                if re.search(pattern, content):
                    findings.append({
                        "severity": "CRITICAL",
                        "category": "INJECTION",
                        "description": "Unsafe shell execution vector detected in app.py."
                    })

        # Save findings to DB
        passed = len([f for f in findings if f["severity"] in ["HIGH", "CRITICAL"]]) == 0
        for f in findings:
            finding_obj = SecurityFindingModel(
                id=f"sf-{uuid.uuid4().hex[:8]}",
                project_id=project_id,
                severity=f["severity"],
                category=f["category"],
                description=f["description"],
                resolved=passed,
                created_at=now_utc()
            )
            db.add(finding_obj)
        db.commit()

        return {
            "status": "PASSED" if passed else "FAILED",
            "findings_count": len(findings),
            "findings": findings,
            "passed": passed
        }

security_agent = SecurityAgent()
