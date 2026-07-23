from pydantic import BaseModel, Field

from app.schemas.analyze import PromptAnalysisResult, ResponseAnalysisResult
from app.schemas.compliance import ComplianceAnalysisResult


class CalculateRiskRequest(BaseModel):
    prompt_analysis: PromptAnalysisResult | None = Field(
        default=None, description="Analysis result of the input prompt."
    )
    response_analysis: ResponseAnalysisResult | None = Field(
        default=None, description="Analysis result of the AI response."
    )
    compliance_analysis: ComplianceAnalysisResult | None = Field(
        default=None, description="Compliance evaluation result."
    )


class RiskScoringResult(BaseModel):
    overall_risk_score: int = Field(ge=0, le=100, description="Weighted overall risk score from 0 (safe) to 100 (critical).")
    risk_level: str = Field(description="Qualitative risk classification: Low, Medium, High, or Critical.")
    privacy_score: int = Field(ge=0, le=100, description="Privacy risk score from 0 to 100.")
    security_score: int = Field(ge=0, le=100, description="Security risk score from 0 to 100.")
    compliance_score: int = Field(ge=0, le=100, description="Compliance risk score from 0 to 100.")
    hallucination_score: int = Field(ge=0, le=100, description="Hallucination risk score from 0 to 100.")
    explanation: list[str] = Field(default_factory=list, description="List of explanations detailing the risk factors.")
