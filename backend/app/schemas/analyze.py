from typing import Any
from pydantic import BaseModel, Field

from app.models.risk_level import RiskLevel


class AnalyzePromptRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=20000, description="The user prompt to analyze.")
    context: dict[str, Any] | None = Field(default=None, description="Optional metadata or context for the prompt.")


class AnalyzeResponseRequest(BaseModel):
    response: str = Field(min_length=1, max_length=20000, description="The AI response to analyze.")
    prompt: str | None = Field(default=None, description="Optional user prompt associated with the response.")
    context: dict[str, Any] | None = Field(default=None, description="Optional context for the response.")


class CategoryMatchDetail(BaseModel):
    pattern_name: str = Field(description="Identifier of the rule or pattern matched.")
    match_text: str = Field(description="Matched text snippet or redacted representation.")
    severity: RiskLevel = Field(description="Severity level associated with this specific match.")


class CategoryAnalysisResult(BaseModel):
    detected: bool = Field(description="Whether risk was detected in this category.")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence level of the detection from 0.0 to 1.0.")
    risk_level: RiskLevel = Field(description="Highest risk level in this category.")
    matches: list[CategoryMatchDetail] = Field(default_factory=list, description="List of specific matched items.")
    explanation: str = Field(description="Human-readable explanation of findings and remediation.")


class PromptAnalysisResult(BaseModel):
    is_safe: bool = Field(description="True if the prompt is considered safe (no high or critical risks).")
    risk_score: float = Field(ge=0.0, le=1.0, description="Overall risk score between 0.0 (safe) and 1.0 (critical risk).")
    risk_level: RiskLevel = Field(description="Overall risk level assessment.")
    summary: str = Field(description="Executive summary of the prompt security evaluation.")
    flagged_categories: list[str] = Field(default_factory=list, description="List of categories flagged for risk.")
    categories: dict[str, CategoryAnalysisResult] = Field(
        description="Detailed breakdown of analysis results per category."
    )
    sanitized_prompt: str = Field(description="Prompt with sensitive information (e.g. PII, secrets) redacted.")


class ResponseAnalysisResult(BaseModel):
    is_safe: bool = Field(description="True if the AI response is safe and compliant (no high or critical risks).")
    risk_score: float = Field(ge=0.0, le=1.0, description="Overall risk score between 0.0 (safe) and 1.0 (critical risk).")
    risk_level: RiskLevel = Field(description="Overall risk level assessment.")
    summary: str = Field(description="Executive summary of the AI response security evaluation.")
    flagged_categories: list[str] = Field(default_factory=list, description="List of categories flagged for risk.")
    categories: dict[str, CategoryAnalysisResult] = Field(
        description="Detailed breakdown of analysis results per category."
    )
    sanitized_response: str = Field(description="AI response with sensitive information (e.g. PII, secrets) redacted.")
