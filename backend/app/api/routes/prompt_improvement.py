from fastapi import APIRouter, Depends, status

from app.schemas.prompt_improvement import ImprovePromptRequest, ImprovePromptResponse
from app.services.prompt_improvement_service import PromptImprovementService

router = APIRouter()


def get_prompt_improvement_service() -> PromptImprovementService:
    return PromptImprovementService()


@router.post(
    "/improve-prompt",
    response_model=ImprovePromptResponse,
    status_code=status.HTTP_200_OK,
    summary="Improve an unsafe prompt for governance and compliance",
    description="Analyzes an unsafe user prompt, identifies security risks, and generates safe, governance-compliant rewrites and alternatives.",
)
def improve_prompt(
    payload: ImprovePromptRequest,
    service: PromptImprovementService = Depends(get_prompt_improvement_service),
) -> ImprovePromptResponse:
    return service.improve_prompt(payload)
