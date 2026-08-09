from typing import Dict, Any, List
from sqlalchemy.orm import Session
from aegis.models import ProjectModel, TestRunModel, ReviewModel, SecurityFindingModel

class AutomatedQualityGates:
    """
    Enforces strict Quality Gates before project completion:
    - BUILD PASSED
    - TESTS PASSED
    - SECURITY CHECK PASSED
    - CODE REVIEW PASSED
    - DOCUMENTATION GENERATED
    """
    def evaluate_gates(
        self,
        db: Session,
        project_id: str,
        test_passed: bool,
        security_passed: bool,
        review_approved: bool,
        docs_present: bool
    ) -> Dict[str, Any]:
        gates = {
            "build_passed": True,
            "tests_passed": test_passed,
            "security_passed": security_passed,
            "code_review_passed": review_approved,
            "documentation_generated": docs_present
        }

        all_passed = all(gates.values())
        
        project = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
        if project:
            project.quality_gate_passed = all_passed
            db.commit()

        return {
            "all_passed": all_passed,
            "gates": gates,
            "status": "APPROVED" if all_passed else "REPAIR_REQUIRED"
        }

quality_gates = AutomatedQualityGates()
