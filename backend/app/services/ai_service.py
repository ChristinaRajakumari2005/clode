from typing import Any, Dict, Optional

from app.services.gemini_service import GeminiService


class AIService:
    """Service layer for orchestrating AI model requests.
    Delegates generation to GeminiService without applying governance rules.
    """

    def __init__(self, gemini_service: Optional[GeminiService] = None):
        self.gemini_service = gemini_service if gemini_service is not None else GeminiService()

    async def generate_response(self, prompt: str) -> Dict[str, Any]:
        """Receives a validated prompt, delegates to GeminiService, and returns the response payload."""
        return await self.gemini_service.generate_response(prompt)
