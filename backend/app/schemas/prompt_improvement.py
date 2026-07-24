from pydantic import BaseModel, Field


class ImprovePromptRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=20000, description="The user prompt to evaluate and improve.")


class ImprovePromptResponse(BaseModel):
    original_prompt: str = Field(description="The original user prompt input.")
    risk_summary: list[str] = Field(default_factory=list, description="List of detected risk categories.")
    unsafe_reason: str = Field(description="Explanation of why the prompt is considered unsafe or safe.")
    improved_prompt: str = Field(description="A safe, governance-compliant version of the prompt.")
    alternative_prompts: list[str] = Field(
        default_factory=list, description="List of alternative safe prompt reformulations."
    )
    message: str | None = Field(default=None, description="Optional status message if prompt is already safe.")
