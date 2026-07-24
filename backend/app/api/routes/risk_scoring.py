from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.risk_scoring import CalculateRiskRequest, RiskScoringResult
from app.services.risk_scoring_service import RiskScoringService

router = APIRouter()


def get_risk_scoring_service() -> RiskScoringService:
    return RiskScoringService()


@router.post(
    "/calculate-risk",
    response_model=RiskScoringResult,
    status_code=status.HTTP_200_OK,
    summary="Calculate unified AI risk score and breakdown",
    description=(
        "Evaluates prompt analysis, response analysis, and compliance evaluation results "
        "to compute overall and categorical risk scores, risk levels, and human-readable explanations."
    ),
)
def calculate_risk(
    payload: CalculateRiskRequest,
    service: RiskScoringService = Depends(get_risk_scoring_service),
) -> RiskScoringResult:
    if (
        payload.prompt_analysis is None
        and payload.response_analysis is None
        and payload.compliance_analysis is None
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one analysis result (prompt_analysis, response_analysis, or compliance_analysis) must be provided.",
        )

    return service.calculate_risk(
        prompt_analysis=payload.prompt_analysis,
        response_analysis=payload.response_analysis,
        compliance_analysis=payload.compliance_analysis,
    )
