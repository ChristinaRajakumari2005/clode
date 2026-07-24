from fastapi import HTTPException, status


class GeminiBaseException(HTTPException):
    """Base exception for Gemini AI service errors."""

    def __init__(self, status_code: int, detail: str, error_type: str = "gemini_error"):
        super().__init__(status_code=status_code, detail=detail)
        self.error_type = error_type


class InvalidAPIKeyError(GeminiBaseException):
    """Raised when the Gemini API key is missing or invalid."""

    def __init__(self, detail: str = "Invalid or missing Gemini API Key."):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_type="invalid_api_key",
        )


class RateLimitError(GeminiBaseException):
    """Raised when Gemini API rate limit is exceeded."""

    def __init__(self, detail: str = "Gemini API rate limit exceeded. Please try again later."):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            error_type="rate_limit_exceeded",
        )


class GeminiTimeoutError(GeminiBaseException):
    """Raised when a request to Gemini API times out."""

    def __init__(self, detail: str = "Request to Gemini API timed out."):
        super().__init__(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=detail,
            error_type="timeout_error",
        )


class GeminiNetworkError(GeminiBaseException):
    """Raised when network failure occurs while connecting to Gemini API."""

    def __init__(self, detail: str = "Network failure while communicating with Gemini API."):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            error_type="network_error",
        )


class GeminiServiceError(GeminiBaseException):
    """Raised when an unexpected exception occurs in Gemini AI service."""

    def __init__(self, detail: str = "An unexpected error occurred in Gemini AI service."):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_type="unexpected_error",
        )
