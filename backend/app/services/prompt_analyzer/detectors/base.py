from abc import ABC, abstractmethod
from typing import Any

from app.schemas.analyze import CategoryAnalysisResult


class BaseDetector(ABC):
    @property
    @abstractmethod
    def category_name(self) -> str:
        """Unique key for the risk category (e.g. 'pii', 'prompt_injection')."""
        pass

    @abstractmethod
    def detect(self, prompt: str, context: dict[str, Any] | None = None) -> CategoryAnalysisResult:
        """Analyzes the prompt and returns a structured CategoryAnalysisResult."""
        pass

    def sanitize(self, prompt: str) -> str:
        """Optional method to redact or mask sensitive content for this detector.

        Returns unchanged prompt by default.
        """
        return prompt
