import asyncio
import logging
import time
from typing import Any, Dict

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

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
    """Service responsible for interacting with the Google Gemini API."""

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()

    def _configure_client(self) -> None:
        """Configures the Gemini API client using settings."""
        api_key = self.settings.gemini_api_key
        if not api_key or not api_key.strip():
            raise InvalidAPIKeyError("GEMINI_API_KEY is not configured in environment or settings.")
        genai.configure(api_key=api_key.strip())

    async def generate_response(self, prompt: str) -> Dict[str, Any]:
        """Generates an AI response from Gemini with timeout, exponential backoff retries,
        and error handling.
        """
        self._configure_client()

        start_time = time.time()
        max_retries = max(1, self.settings.max_retries)
        initial_delay = 1.0
        retry_count = 0

        generation_config = genai.GenerationConfig(
            temperature=self.settings.temperature,
            max_output_tokens=self.settings.max_output_tokens,
        )

        model = genai.GenerativeModel(
            model_name=self.settings.model_name,
            generation_config=generation_config,
        )

        for attempt in range(max_retries):
            try:
                response = await asyncio.wait_for(
                    model.generate_content_async(prompt),
                    timeout=self.settings.request_timeout,
                )

                response_text = ""
                if hasattr(response, "text") and response.text:
                    response_text = response.text
                elif hasattr(response, "parts") and response.parts:
                    response_text = "".join(part.text for part in response.parts if hasattr(part, "text"))

                total_duration = time.time() - start_time
                iso_timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

                logger.info(
                    f"Gemini API Request Succeeded | Timestamp: {iso_timestamp} | "
                    f"Duration: {total_duration:.4f}s | Retries: {retry_count} | Model: {self.settings.model_name}"
                )

                return {
                    "response": response_text,
                    "model": self.settings.model_name,
                    "status": "success",
                }

            except (google_exceptions.Unauthenticated, google_exceptions.PermissionDenied) as e:
                logger.error("Gemini API authentication failed (Invalid API Key).")
                raise InvalidAPIKeyError("Invalid Gemini API Key or unauthorized request.") from e

            except (google_exceptions.ResourceExhausted, google_exceptions.TooManyRequests) as e:
                if attempt < max_retries - 1:
                    retry_count += 1
                    backoff = initial_delay * (2**attempt)
                    logger.warning(f"Rate limit hit. Retrying attempt {attempt + 1}/{max_retries} in {backoff:.2f}s...")
                    await asyncio.sleep(backoff)
                    continue
                logger.error("Gemini API rate limit exceeded.")
                raise RateLimitError() from e

            except (asyncio.TimeoutError, google_exceptions.DeadlineExceeded) as e:
                if attempt < max_retries - 1:
                    retry_count += 1
                    backoff = initial_delay * (2**attempt)
                    logger.warning(f"Request timed out. Retrying attempt {attempt + 1}/{max_retries} in {backoff:.2f}s...")
                    await asyncio.sleep(backoff)
                    continue
                logger.error("Gemini API request timed out.")
                raise GeminiTimeoutError() from e

            except (google_exceptions.ServiceUnavailable, ConnectionError, OSError) as e:
                if attempt < max_retries - 1:
                    retry_count += 1
                    backoff = initial_delay * (2**attempt)
                    logger.warning(f"Network error occurred. Retrying attempt {attempt + 1}/{max_retries} in {backoff:.2f}s...")
                    await asyncio.sleep(backoff)
                    continue
                logger.error("Network failure while connecting to Gemini API.")
                raise GeminiNetworkError() from e

            except google_exceptions.InvalidArgument as e:
                err_msg = str(e).lower()
                if "api key" in err_msg or "apikey" in err_msg or "key" in err_msg:
                    raise InvalidAPIKeyError("Invalid Gemini API Key.") from e
                raise GeminiServiceError(f"Invalid request argument: {str(e)}") from e

            except Exception as e:
                err_msg = str(e).lower()
                if "api_key" in err_msg or "apikey" in err_msg or "unauthenticated" in err_msg:
                    raise InvalidAPIKeyError("Invalid Gemini API Key.") from e
                if "quota" in err_msg or "rate limit" in err_msg or "429" in err_msg:
                    if attempt < max_retries - 1:
                        retry_count += 1
                        backoff = initial_delay * (2**attempt)
                        await asyncio.sleep(backoff)
                        continue
                    raise RateLimitError() from e

                if attempt < max_retries - 1:
                    retry_count += 1
                    backoff = initial_delay * (2**attempt)
                    await asyncio.sleep(backoff)
                    continue

                logger.error(f"Unexpected error in Gemini API service: {type(e).__name__}")
                raise GeminiServiceError(f"Unexpected error: {str(e)}") from e
