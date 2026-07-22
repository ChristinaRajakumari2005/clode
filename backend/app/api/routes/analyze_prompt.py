from fastapi import APIRouter, status

from app.schemas.analyze import AnalyzePromptRequest, PromptAnalysisResult
from app.services.prompt_analysis_service import PromptAnalysisService

router = APIRouter()


@router.post(
    "/analyze-prompt",
    response_model=PromptAnalysisResult,
    status_code=status.HTTP_200_OK,
    summary="Analyze a prompt for governance and compliance risks",
    description=(
        "Performs rule-based detection for PII, prompt injection, jailbreak attempts, "
        "toxic language, unsafe requests, company secrets, and compliance issues."
    ),
)
def analyze_prompt(payload: AnalyzePromptRequest) -> PromptAnalysisResult:
    service = PromptAnalysisService()
    return service.analyze_prompt(payload)
