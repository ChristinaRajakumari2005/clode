from typing import Any

from app.models.risk_level import RiskLevel
from app.schemas.analyze import CategoryAnalysisResult, ResponseAnalysisResult
from app.services.response_analyzer.detectors.base import BaseResponseDetector
from app.services.response_analyzer.detectors.bias_detector import BiasDetector
from app.services.response_analyzer.detectors.compliance_detector import ComplianceDetector
from app.services.response_analyzer.detectors.hallucination_detector import HallucinationDetector
from app.services.response_analyzer.detectors.sensitive_info_detector import SensitiveInfoDetector
from app.services.response_analyzer.detectors.toxicity_detector import ToxicityDetector
from app.services.response_analyzer.detectors.unsafe_content_detector import UnsafeContentDetector


class ResponseAnalyzer:
    def __init__(self) -> None:
        self.detectors: list[BaseResponseDetector] = [
            HallucinationDetector(),
            BiasDetector(),
            ToxicityDetector(),
            SensitiveInfoDetector(),
            UnsafeContentDetector(),
            ComplianceDetector(),
        ]

    def analyze_response(
        self,
        response: str,
        prompt: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> ResponseAnalysisResult:
        categories: dict[str, CategoryAnalysisResult] = {}
        flagged_categories: list[str] = []
        highest_risk = RiskLevel.LOW

        sanitized_response = response

        for detector in self.detectors:
            result = detector.detect(response, prompt=prompt, context=context)
            categories[detector.category_name] = result

            if result.detected:
                flagged_categories.append(detector.category_name)
                if self._severity_weight(result.risk_level) > self._severity_weight(highest_risk):
                    highest_risk = result.risk_level

            # Apply detector sanitization if available
            sanitized_response = detector.sanitize(sanitized_response)

        # Calculate overall risk score (0.0 to 1.0)
        risk_score = self._calculate_risk_score(categories, highest_risk)

        # Determine is_safe status
        is_safe = highest_risk not in (RiskLevel.HIGH, RiskLevel.CRITICAL) and len(flagged_categories) == 0

        # Generate summary
        if len(flagged_categories) == 0:
            summary = "AI response is safe, unbiased, and compliant with all rule-based governance checks."
        else:
            summary = (
                f"AI response flagged for risks in [{', '.join(flagged_categories)}]. "
                f"Overall Risk Level: {highest_risk.value.upper()} (Score: {risk_score:.2f})."
            )

        return ResponseAnalysisResult(
            is_safe=is_safe,
            risk_score=risk_score,
            risk_level=highest_risk,
            summary=summary,
            flagged_categories=flagged_categories,
            categories=categories,
            sanitized_response=sanitized_response,
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

        flagged_count = sum(1 for res in categories.values() if res.detected)
        if flagged_count > 1 and score < 1.0:
            score = min(1.0, score + (flagged_count - 1) * 0.08)

        return round(score, 2)

    def _severity_weight(self, severity: RiskLevel) -> int:
        weights = {RiskLevel.LOW: 1, RiskLevel.MODERATE: 2, RiskLevel.HIGH: 3, RiskLevel.CRITICAL: 4}
        return weights.get(severity, 0)
