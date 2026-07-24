import logging
from typing import Any, Dict

from google import genai
from google.genai import types

from app.config.settings import Settings, get_settings
from app.utils.api_exceptions import (
    GeminiNetworkError,
    GeminiServiceError,
    GeminiTimeoutError,
    InvalidAPIKeyError,
    RateLimitError,
)

logger = logging.getLogger(__name__)


class GeminiService:

    def __init__(self, settings: Settings | None = None):

        self.settings = settings or get_settings()

        print("=" * 80)
        print("Using NEW Google GenAI SDK")
        print("Model :", self.settings.model_name)
        print("Key length :", len(self.settings.gemini_api_key))
        print("=" * 80)

        self.client = genai.Client(
            api_key=self.settings.gemini_api_key.strip()
        )


    async def generate_response(self, prompt: str) -> Dict[str, Any]:

        try:

            response = self.client.models.generate_content(
                model=self.settings.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=self.settings.temperature,
                    max_output_tokens=self.settings.max_output_tokens,
                ),
            )

            return {
                "response": response.text,
                "model": self.settings.model_name,
                "status": "success",
            }


        except Exception as e:

            print("\nGENAI SDK ERROR")
            print(type(e).__name__)
            print(e)

            msg = str(e).lower()

            if "permissiondenied" in msg or "403" in msg:
                raise InvalidAPIKeyError(
                    "Invalid Gemini API Key or unauthorized request."
                ) from e

            if "quota" in msg or "429" in msg:
                raise RateLimitError() from e

            if "timeout" in msg:
                raise GeminiTimeoutError() from e

            if "network" in msg:
                raise GeminiNetworkError() from e

            raise GeminiServiceError(str(e)) from e