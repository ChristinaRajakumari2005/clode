from fastapi import APIRouter, status

from app.schemas.analyze import AnalyzeResponseRequest, ResponseAnalysisResult
from app.services.response_analysis_service import ResponseAnalysisService

router = APIRouter()


@router.post(
    "/analyze-response",
    response_model=ResponseAnalysisResult,
    status_code=status.HTTP_200_OK,
    summary="Analyze an AI response for governance, bias, toxicity, and compliance risks",
    description=(
        "Performs rule-based detection on AI responses for hallucination risk, bias, "
        "toxicity, sensitive information leakage, unsafe content, and compliance violations."
    ),
)
def analyze_response(payload: AnalyzeResponseRequest) -> ResponseAnalysisResult:
    service = ResponseAnalysisService()
    return service.analyze_response(payload)
