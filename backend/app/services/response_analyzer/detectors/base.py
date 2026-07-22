from abc import ABC, abstractmethod
from typing import Any

from app.schemas.analyze import CategoryAnalysisResult


class BaseResponseDetector(ABC):
    @property
    @abstractmethod
    def category_name(self) -> str:
        """Unique key for the response risk category (e.g. 'hallucination_risk', 'bias')."""
        pass

    @abstractmethod
    def detect(
        self,
        response: str,
        prompt: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> CategoryAnalysisResult:
        """Analyzes the AI response (and optional user prompt) and returns a CategoryAnalysisResult."""
        pass

    def sanitize(self, response: str) -> str:
        """Optional method to redact or mask sensitive content for this detector in the AI response."""
        return response
