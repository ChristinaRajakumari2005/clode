from typing import Any, List, Optional
from pydantic import BaseModel, Field

from app.schemas.analyze import PromptAnalysisResult, ResponseAnalysisResult
from app.schemas.compliance import ComplianceAnalysisResult
from app.schemas.hallucination import DetectHallucinationResponse
from app.schemas.risk_scoring import RiskScoringResult


class GenerateAuditReportRequest(BaseModel):
    prompt_analysis: Optional[PromptAnalysisResult] = Field(
        default=None, description="Outcome of prompt security analysis."
    )
    response_analysis: Optional[ResponseAnalysisResult] = Field(
        default=None, description="Outcome of response security analysis."
    )
    compliance_analysis: Optional[ComplianceAnalysisResult] = Field(
        default=None, description="Outcome of compliance evaluation."
    )
    risk_scoring: Optional[RiskScoringResult] = Field(
        default=None, description="Outcome of risk scoring calculation."
    )
    hallucination_analysis: Optional[DetectHallucinationResponse] = Field(
        default=None, description="Outcome of hallucination detection."
    )


class ReportSections(BaseModel):
    prompt_analysis: Any = Field(description="Summary and findings for prompt security analysis.")
    response_analysis: Any = Field(description="Summary and findings for response security analysis.")
    compliance: Any = Field(description="Summary and policy violations for compliance evaluation.")
    hallucination: Any = Field(description="Summary and flagged claims for hallucination detection.")
    risk_scoring: Any = Field(description="Breakdown of component and overall risk scores.")


class GenerateAuditReportResponse(BaseModel):
    report_id: str = Field(description="Unique UUID identifier for the audit report.")
    generated_at: str = Field(description="ISO8601 UTC timestamp of report generation.")
    overall_status: str = Field(description="Governance status: PASS, WARNING, or FAIL.")
    executive_summary: str = Field(description="High-level executive summary of audit findings.")
    overall_risk_score: int = Field(ge=0, le=100, description="Overall risk score from 0 to 100.")
    risk_level: str = Field(description="Categorical risk level: Low, Medium, High, or Critical.")
    sections: ReportSections = Field(description="Structured breakdowns for each governance area.")
    recommendations: List[str] = Field(default_factory=list, description="Actionable recommendations.")
