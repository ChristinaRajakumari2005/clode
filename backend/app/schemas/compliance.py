from typing import Any
from pydantic import BaseModel, Field
from app.models.risk_level import RiskLevel


class ComplianceViolation(BaseModel):
    name: str = Field(description="Name of the violated policy.")
    description: str = Field(description="Description of the policy.")
    severity: RiskLevel = Field(description="Severity of the violation.")
    reason: str = Field(description="Reason why the content violates the policy.")
    recommendation: str = Field(description="Recommendation for remediation.")
    matched_text: str = Field(description="Snippet of text that triggered the violation.")
    start_index: int = Field(description="Starting index of the violation in the text.")
    end_index: int = Field(description="Ending index of the violation in the text.")


class EvaluateComplianceRequest(BaseModel):
    content: str = Field(min_length=1, max_length=50000, description="The content to scan for compliance violations.")
    context: dict[str, Any] | None = Field(default=None, description="Optional metadata or context.")


class ComplianceAnalysisResult(BaseModel):
    is_compliant: bool = Field(description="True if no violations were found.")
    violations: list[ComplianceViolation] = Field(default_factory=list, description="List of detected policy violations.")
    risk_level: RiskLevel = Field(description="Highest risk level among the matched violations.")
