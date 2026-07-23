from fastapi import APIRouter, Depends, status

from app.schemas.hallucination import DetectHallucinationRequest, DetectHallucinationResponse
from app.services.hallucination_service import HallucinationService

router = APIRouter()


def get_hallucination_service() -> HallucinationService:
    return HallucinationService()


@router.post(
    "/detect-hallucination",
    response_model=DetectHallucinationResponse,
    status_code=status.HTTP_200_OK,
    summary="Detect potential hallucinations in AI responses",
    description="Performs rule-based heuristic detection for factual inconsistencies, absolute statements, unsupported numerical claims, and empty or fabricated citations in AI text.",
)
def detect_hallucination(
    payload: DetectHallucinationRequest,
    service: HallucinationService = Depends(get_hallucination_service),
) -> DetectHallucinationResponse:
    return service.detect_hallucination(payload)
