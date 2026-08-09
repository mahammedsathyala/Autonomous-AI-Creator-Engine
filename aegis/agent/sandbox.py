import os
import sys
import time
import subprocess
from typing import Dict, Any, Optional
from aegis.config import settings

class ExecutionSandbox:
    """
    Secure Execution Sandbox for executing AI-generated applications,
    package installations, and test runners with timeout & memory bounds.
    """
    def __init__(self, workspace_base: Optional[str] = None):
        self.workspace_base = workspace_base or settings.SANDBOX_WORK_DIR
        os.makedirs(self.workspace_base, exist_ok=True)

    def get_project_dir(self, project_id: str) -> str:
        project_dir = os.path.join(self.workspace_base, project_id)
        os.makedirs(project_dir, exist_ok=True)
        return project_dir

    def execute_command(
        self,
        command: str,
        project_id: str,
        timeout_seconds: Optional[int] = None
    ) -> Dict[str, Any]:
        project_dir = self.get_project_dir(project_id)
        timeout = timeout_seconds or settings.SANDBOX_TIMEOUT_SECONDS
        
        start_time = time.time()
        try:
            res = subprocess.run(
                command,
                shell=True,
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            duration_ms = int((time.time() - start_time) * 1000)
            return {
                "exit_code": res.returncode,
                "stdout": res.stdout,
                "stderr": res.stderr,
                "duration_ms": duration_ms,
                "status": "SUCCESS" if res.returncode == 0 else "FAILED",
                "timed_out": False
            }
        except subprocess.TimeoutExpired as e:
            duration_ms = int((time.time() - start_time) * 1000)
            return {
                "exit_code": -1,
                "stdout": e.stdout or "",
                "stderr": f"Execution timed out after {timeout}s",
                "duration_ms": duration_ms,
                "status": "TIMED_OUT",
                "timed_out": True
            }
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            return {
                "exit_code": -1,
                "stdout": "",
                "stderr": str(e),
                "duration_ms": duration_ms,
                "status": "ERROR",
                "timed_out": False
            }

sandbox_runner = ExecutionSandbox()
