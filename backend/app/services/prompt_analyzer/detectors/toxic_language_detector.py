import re
from typing import Any

from app.models.risk_level import RiskLevel
from app.schemas.analyze import CategoryAnalysisResult, CategoryMatchDetail
from app.services.prompt_analyzer.detectors.base import BaseDetector


class ToxicLanguageDetector(BaseDetector):
    @property
    def category_name(self) -> str:
        return "toxic_language"

    TOXIC_PATTERNS: list[tuple[str, str, RiskLevel, str]] = [
        # Explicit Harassment & Violence Directives
        (
            "self_harm_encouragement",
            r"(?i)\b(?:kill\s+yourself|go\s+die|commit\s+suicide|end\s+your\s+life)\b",
            RiskLevel.CRITICAL,
            "Self-harm encouragement or suicide instruction directed at individuals.",
        ),
        (
            "violent_threat",
            r"(?i)\b(?:i\s+will|i'm\s+going\s+to)\s+(?:kill|murder|attack|stab|shoot|slaughter|bomb|hurt)\s+(?:you|them|him|her)\b",
            RiskLevel.CRITICAL,
            "Direct violent threat or attack intention.",
        ),
        # Severe Harassment / Abuse
        (
            "severe_harassment",
            r"(?i)\b(?:you\s+are\s+worthless|nobody\s+likes\s+you|hope\s+you\s+get\s+cancer|go\s+burn\s+in\s+hell)\b",
            RiskLevel.HIGH,
            "Severe harassment or abusive insult pattern.",
        ),
        # Profanity & Obscenity Keywords
        (
            "profanity",
            r"(?i)\b(?:fuck|shit|bitch|cunt|asshole|bastard|dickhead|motherfucker)\b",
            RiskLevel.MODERATE,
            "Explicit profanity or vulgar language.",
        ),
        # Hate Speech & Slurs
        (
            "hate_slur",
            r"(?i)\b(?:nigger|faggot|kike|chink|spic|retard|wetback)\b",
            RiskLevel.CRITICAL,
            "Hate speech slur or discriminatory slur.",
        ),
    ]

    def detect(self, prompt: str, context: dict[str, Any] | None = None) -> CategoryAnalysisResult:
        matches: list[CategoryMatchDetail] = []
        highest_risk = RiskLevel.LOW

        for pattern_name, pattern_regex, severity, _desc in self.TOXIC_PATTERNS:
            found = re.finditer(pattern_regex, prompt)
            for m in found:
                match_str = m.group(0)
                # Redact slurs/profanity slightly in match_text to keep logs clean
                masked = match_str[0] + "*" * (len(match_str) - 2) + match_str[-1] if len(match_str) > 2 else "**"
                matches.append(
                    CategoryMatchDetail(
                        pattern_name=pattern_name,
                        match_text=masked,
                        severity=severity,
                    )
                )
                if self._severity_weight(severity) > self._severity_weight(highest_risk):
                    highest_risk = severity

        detected = len(matches) > 0
        confidence = 0.90 if detected else 0.0

        if detected:
            toxic_types = list({m.pattern_name for m in matches})
            explanation = (
                f"Toxic language detected ({', '.join(toxic_types)}). "
                "Prompt contains profanity, hate speech, threats, or severe harassment."
            )
        else:
            explanation = "No toxic language or profanity detected."

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
