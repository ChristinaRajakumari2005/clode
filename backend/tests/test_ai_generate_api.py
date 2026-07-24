from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.utils.api_exceptions import (
    InvalidAPIKeyError,
    RateLimitError,
    GeminiTimeoutError,
    GeminiNetworkError,
    GeminiServiceError,
)

client = TestClient(app)


def test_generate_ai_response_success():
    mock_service_response = {
        "response": "Hello! This is a test AI response from Gemini.",
        "model": "gemini-2.5-flash",
        "status": "success",
    }
    with patch("app.api.routes.ai_generate.AIService.generate_response", new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = mock_service_response

        response = client.post("/generate-ai-response", json={"prompt": "Hello Gemini"})
        assert response.status_code == 200
        data = response.json()
        assert data["response"] == "Hello! This is a test AI response from Gemini."
        assert data["model"] == "gemini-2.5-flash"
        assert data["status"] == "success"


def test_generate_ai_response_invalid_key():
    with patch("app.api.routes.ai_generate.AIService.generate_response", new_callable=AsyncMock) as mock_gen:
        mock_gen.side_effect = InvalidAPIKeyError("Invalid Gemini API Key.")

        response = client.post("/generate-ai-response", json={"prompt": "Test prompt"})
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid Gemini API Key."


def test_generate_ai_response_rate_limit():
    with patch("app.api.routes.ai_generate.AIService.generate_response", new_callable=AsyncMock) as mock_gen:
        mock_gen.side_effect = RateLimitError("Gemini API rate limit exceeded. Please try again later.")

        response = client.post("/generate-ai-response", json={"prompt": "Test prompt"})
        assert response.status_code == 429
        assert "rate limit" in response.json()["detail"].lower()


def test_generate_ai_response_timeout():
    with patch("app.api.routes.ai_generate.AIService.generate_response", new_callable=AsyncMock) as mock_gen:
        mock_gen.side_effect = GeminiTimeoutError("Request to Gemini API timed out.")

        response = client.post("/generate-ai-response", json={"prompt": "Test prompt"})
        assert response.status_code == 504
        assert "timed out" in response.json()["detail"].lower()


def test_generate_ai_response_network_error():
    with patch("app.api.routes.ai_generate.AIService.generate_response", new_callable=AsyncMock) as mock_gen:
        mock_gen.side_effect = GeminiNetworkError("Network failure while communicating with Gemini API.")

        response = client.post("/generate-ai-response", json={"prompt": "Test prompt"})
        assert response.status_code == 503
        assert "network failure" in response.json()["detail"].lower()


def test_generate_ai_response_unexpected_error():
    with patch("app.api.routes.ai_generate.AIService.generate_response", new_callable=AsyncMock) as mock_gen:
        mock_gen.side_effect = GeminiServiceError("An unexpected error occurred in Gemini AI service.")

        response = client.post("/generate-ai-response", json={"prompt": "Test prompt"})
        assert response.status_code == 500
        assert "unexpected error" in response.json()["detail"].lower()
