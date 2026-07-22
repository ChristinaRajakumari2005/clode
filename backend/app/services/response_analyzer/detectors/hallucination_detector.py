import re
from typing import Any

from app.models.risk_level import RiskLevel
from app.schemas.analyze import CategoryAnalysisResult, CategoryMatchDetail
from app.services.response_analyzer.detectors.base import BaseResponseDetector


class HallucinationDetector(BaseResponseDetector):
    @property
    def category_name(self) -> str:
        return "hallucination_risk"

    PATTERNS: list[tuple[str, str, RiskLevel, str]] = [
        # Absolute Overconfidence Claims
        (
            "unsubstantiated_certainty",
            r"(?i)\b(?:100%\s+(?:certain|guaranteed|indisputable|proven)|absolute\s+undeniable\s+fact|it\s+is\s+a\s+proven\s+fact\s+without\s+doubt)\b",
            RiskLevel.HIGH,
            "Overconfident, unsubstantiated absolute certainty claim.",
        ),
        # Fabricated Citation / Fake DOI / Invalid Reference Patterns
        (
            "fake_doi_citation",
            r"(?i)\bdoi:10\.(?:9999|0000|12345|00000)\/[^\s]+\b",
            RiskLevel.HIGH,
            "Fabricated or placeholder DOI citation pattern.",
        ),
        (
            "fake_source_url",
            r"(?i)\bhttps?:\/\/(?:www\.)?(?:fake-source|nonexistent-domain|example-citation-link-[0-9]+)\.(?:org|com|edu)\b",
            RiskLevel.HIGH,
            "Synthetic or fake reference URL pattern detected.",
        ),
        (
            "future_citation_year",
            r"(?i)\[[A-Z][a-z]+(?:\s+et\s+al\.)?,\s*(?:20[3-9][0-9]|21[0-9]{2})\]",
            RiskLevel.HIGH,
            "Anachronistic or future publication year citation.",
        ),
    ]

    def detect(
        self,
        response: str,
        prompt: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> CategoryAnalysisResult:
        matches: list[CategoryMatchDetail] = []
        highest_risk = RiskLevel.LOW

        # 1. Regex rule checks
        for pattern_name, pattern_regex, severity, _desc in self.PATTERNS:
            found = re.finditer(pattern_regex, response)
            for m in found:
                match_str = m.group(0)
                matches.append(
                    CategoryMatchDetail(
                        pattern_name=pattern_name,
                        match_text=match_str[:80],
                        severity=severity,
                    )
                )
                if self._severity_weight(severity) > self._severity_weight(highest_risk):
                    highest_risk = severity

        # 2. Prompt-Response Contradiction / Divergence Heuristics
        if prompt:
            prompt_years = set(re.findall(r"\b(19\d\d|20[0-2]\d)\b", prompt))
            response_years = set(re.findall(r"\b(19\d\d|20[0-2]\d)\b", response))

            # If prompt specifically mentions a year (e.g. 1995) and response asserts a completely different historical year without mentioning prompt year
            if prompt_years and response_years and not (prompt_years & response_years):
                matches.append(
                    CategoryMatchDetail(
                        pattern_name="temporal_contradiction",
                        match_text=f"Prompt years {list(prompt_years)} vs Response years {list(response_years)}",
                        severity=RiskLevel.MODERATE,
                    )
                )
                if self._severity_weight(RiskLevel.MODERATE) > self._severity_weight(highest_risk):
                    highest_risk = RiskLevel.MODERATE

        detected = len(matches) > 0
        confidence = 0.85 if detected else 0.0

        if detected:
            hallucination_types = list({m.pattern_name for m in matches})
            explanation = (
                f"Hallucination risk indicators detected ({', '.join(hallucination_types)}). "
                "AI response contains unsubstantiated claims, fake citations, or prompt-response contradictions."
            )
        else:
            explanation = "No obvious hallucination patterns or fake citations detected."

        return CategoryAnalysisResult(
            detected=detected,
            confidence=confidence,
            risk_level=highest_risk,
            matches=matches,
            explanation=explanation,
        )

    def _severity_weight(self, severity: RiskLevel) -> int:
        weights = {RiskLevel.LOW: 1, RiskLevel.MODERATE: 2, RiskLevel.HIGH: 3, RiskLevel.CRITICAL: 4}
        return weights.get(severity, 0)
