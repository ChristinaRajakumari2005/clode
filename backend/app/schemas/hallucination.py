from pydantic import BaseModel, Field


class DetectHallucinationRequest(BaseModel):
    response: str = Field(..., min_length=1, max_length=50000, description="The AI-generated response text to evaluate for hallucinations.")


class FlaggedClaim(BaseModel):
    claim: str = Field(description="The specific statement or claim flagged as a potential hallucination.")
    reason: str = Field(description="Reason why the statement was flagged.")


class DetectHallucinationResponse(BaseModel):
    hallucination_detected: bool = Field(description="True if potential hallucinations or unsupported claims were detected.")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score from 0.0 to 1.0.")
    risk_level: str = Field(description="Qualitative risk classification: Low, Medium, High, or Critical.")
    summary: str = Field(description="Executive summary of the hallucination evaluation.")
    flagged_claims: list[FlaggedClaim] = Field(default_factory=list, description="List of flagged claims and reasons.")
    recommendation: str = Field(description="Actionable recommendation for remediation or verification.")
