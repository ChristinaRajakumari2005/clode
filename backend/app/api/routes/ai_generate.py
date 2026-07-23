from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field

from app.services.ai_service import AIService

router = APIRouter()


class AIGenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="The input prompt for AI response generation")


class AIGenerateResponse(BaseModel):
    response: str = Field(..., description="Generated text response from the AI model")
    model: str = Field(..., description="Name of the model used for response generation")
    status: str = Field(default="success", description="Status of the generation request")


def get_ai_service() -> AIService:
    return AIService()


@router.post(
    "/generate-ai-response",
    response_model=AIGenerateResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate AI Response using Gemini",
    description="Receives a prompt, calls the Gemini AI service, and returns the generated AI response.",
)
async def generate_ai_response(
    payload: AIGenerateRequest,
    ai_service: AIService = Depends(get_ai_service),
) -> AIGenerateResponse:
    result = await ai_service.generate_response(payload.prompt)
    return AIGenerateResponse(**result)
