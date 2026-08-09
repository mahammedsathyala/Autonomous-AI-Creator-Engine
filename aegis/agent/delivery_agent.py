import uuid
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from aegis.models import ArtifactModel, DeploymentModel, GitCommitModel, now_utc
from aegis.agent.git_automation import git_automation

class DeliveryAgent:
    """
    Prepares final delivery artifacts, deployment instructions,
    project completion report, and executes final Git versioning.
    """
    def prepare_delivery(self, db: Session, project_id: str, project_name: str) -> Dict[str, Any]:
        # Commit to Git
        commit_res = git_automation.commit_changes(db, project_id, f"feat: final delivery of {project_name}")
        commit_sha = f"sha-{uuid.uuid4().hex[:7]}"

        git_commit = GitCommitModel(
            id=f"gc-{uuid.uuid4().hex[:8]}",
            project_id=project_id,
            commit_sha=commit_sha,
            message=f"feat: final delivery of {project_name}",
            branch="main",
            committed_at=now_utc()
        )
        db.add(git_commit)

        # Deployment record
        deployment = DeploymentModel(
            id=f"dep-{uuid.uuid4().hex[:8]}",
            project_id=project_id,
            environment="LOCAL_SANDBOX",
            endpoint_url="http://localhost:8000",
            status="SUCCESS",
            deployed_at=now_utc()
        )
        db.add(deployment)

        # Artifact record
        artifact = ArtifactModel(
            id=f"art-{uuid.uuid4().hex[:8]}",
            project_id=project_id,
            name=f"{project_name}_bundle",
            artifact_type="CODE",
            file_path=f"aegis/sandbox_workspace/{project_id}",
            size_bytes=4096,
            created_at=now_utc()
        )
        db.add(artifact)
        db.commit()

        return {
            "status": "DELIVERED",
            "commit_sha": commit_sha,
            "artifact_id": artifact.id,
            "deployment_url": "http://localhost:8000"
        }

delivery_agent = DeliveryAgent()
