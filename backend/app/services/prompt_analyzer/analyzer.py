from typing import Any

from app.models.risk_level import RiskLevel
from app.schemas.analyze import CategoryAnalysisResult, PromptAnalysisResult
from app.services.prompt_analyzer.detectors.base import BaseDetector
from app.services.prompt_analyzer.detectors.company_secrets_detector import CompanySecretsDetector
from app.services.prompt_analyzer.detectors.compliance_detector import ComplianceDetector
from app.services.prompt_analyzer.detectors.jailbreak_detector import JailbreakDetector
from app.services.prompt_analyzer.detectors.pii_detector import PIIDetector
from app.services.prompt_analyzer.detectors.prompt_injection_detector import PromptInjectionDetector
from app.services.prompt_analyzer.detectors.toxic_language_detector import ToxicLanguageDetector
from app.services.prompt_analyzer.detectors.unsafe_requests_detector import UnsafeRequestsDetector


class PromptAnalyzer:
    def __init__(self) -> None:
        self.detectors: list[BaseDetector] = [
            PIIDetector(),
            PromptInjectionDetector(),
            JailbreakDetector(),
            ToxicLanguageDetector(),
            UnsafeRequestsDetector(),
            CompanySecretsDetector(),
            ComplianceDetector(),
        ]

    def analyze_prompt(
        self, prompt: str, context: dict[str, Any] | None = None
    ) -> PromptAnalysisResult:
        categories: dict[str, CategoryAnalysisResult] = {}
        flagged_categories: list[str] = []
        highest_risk = RiskLevel.LOW

        sanitized_prompt = prompt

        for detector in self.detectors:
            result = detector.detect(prompt, context=context)
            categories[detector.category_name] = result

            if result.detected:
                flagged_categories.append(detector.category_name)
                if self._severity_weight(result.risk_level) > self._severity_weight(highest_risk):
                    highest_risk = result.risk_level

            # Apply detector sanitization if available
            sanitized_prompt = detector.sanitize(sanitized_prompt)

        # Calculate overall risk score (0.0 to 1.0)
        risk_score = self._calculate_risk_score(categories, highest_risk)

        # Determine is_safe status
        is_safe = highest_risk not in (RiskLevel.HIGH, RiskLevel.CRITICAL) and len(flagged_categories) == 0

        # Generate summary
        if len(flagged_categories) == 0:
            summary = "Prompt is safe and passed all rule-based governance and security checks."
        else:
            summary = (
                f"Prompt flagged for risks in [{', '.join(flagged_categories)}]. "
                f"Overall Risk Level: {highest_risk.value.upper()} (Score: {risk_score:.2f})."
            )

        return PromptAnalysisResult(
            is_safe=is_safe,
            risk_score=risk_score,
            risk_level=highest_risk,
            summary=summary,
            flagged_categories=flagged_categories,
            categories=categories,
            sanitized_prompt=sanitized_prompt,
        )

    def _calculate_risk_score(
        self, categories: dict[str, CategoryAnalysisResult], highest_risk: RiskLevel
    ) -> float:
        base_weights = {
            RiskLevel.LOW: 0.0,
            RiskLevel.MODERATE: 0.35,
            RiskLevel.HIGH: 0.75,
            RiskLevel.CRITICAL: 1.0,
        }
        score = base_weights.get(highest_risk, 0.0)

        # Add small increment for multiple flagged categories
        flagged_count = sum(1 for res in categories.values() if res.detected)
        if flagged_count > 1 and score < 1.0:
            score = min(1.0, score + (flagged_count - 1) * 0.08)

        return round(score, 2)

    def _severity_weight(self, severity: RiskLevel) -> int:
        weights = {RiskLevel.LOW: 1, RiskLevel.MODERATE: 2, RiskLevel.HIGH: 3, RiskLevel.CRITICAL: 4}
        return weights.get(severity, 0)
