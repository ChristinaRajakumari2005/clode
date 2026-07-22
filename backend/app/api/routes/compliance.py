from fastapi import APIRouter, status
from app.schemas.compliance import EvaluateComplianceRequest, ComplianceAnalysisResult
from app.services.compliance_engine import ComplianceEngine

router = APIRouter()


@router.post(
    "/analyze-compliance",
    response_model=ComplianceAnalysisResult,
    status_code=status.HTTP_200_OK,
    summary="Evaluate text content against GDPR, HIPAA, PCI-DSS, and Company compliance policies",
    description="Evaluates input text against predefined policies and returns a detailed report of matched violations.",
)
def analyze_compliance(payload: EvaluateComplianceRequest) -> ComplianceAnalysisResult:
    engine = ComplianceEngine()
    return engine.evaluate(payload.content, payload.context)
