import re
from typing import Any

from app.models.risk_level import RiskLevel
from app.schemas.analyze import CategoryAnalysisResult, CategoryMatchDetail
from app.services.response_analyzer.detectors.base import BaseResponseDetector


class ToxicityDetector(BaseResponseDetector):
    @property
    def category_name(self) -> str:
        return "toxicity"

    TOXICITY_PATTERNS: list[tuple[str, str, RiskLevel, str]] = [
        # User-Directed Condescending Insults
        (
            "user_directed_insult",
            r"(?i)\b(?:you\s+are\s+(?:stupid|idiot|dumb|ignorant|moron)|that\s+is\s+a\s+stupid\s+question|shut\s+up)\b",
            RiskLevel.HIGH,
            "Condescending insult or offensive statement directed at the user.",
        ),
        # Profanity & Obscenity
        (
            "response_profanity",
            r"(?i)\b(?:fuck|shit|bitch|cunt|asshole|bastard|dickhead|motherfucker)\b",
            RiskLevel.MODERATE,
            "Profanity or vulgar language in AI output.",
        ),
        # Hate Speech Slurs
        (
            "response_hate_slur",
            r"(?i)\b(?:nigger|faggot|kike|chink|spic|retard|wetback)\b",
            RiskLevel.CRITICAL,
            "Hate speech slur in AI output.",
        ),
        # Hostile Aggression / Threats
        (
            "hostile_aggression",
            r"(?i)\b(?:go\s+die|kill\s+yourself|hope\s+you\s+fail|you\s+deserve\s+to\s+suffers?)\b",
            RiskLevel.CRITICAL,
            "Severe hostility or threat in AI output.",
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

        for pattern_name, pattern_regex, severity, _desc in self.TOXICITY_PATTERNS:
            found = re.finditer(pattern_regex, response)
            for m in found:
                match_str = m.group(0)
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
        confidence = 0.95 if detected else 0.0

        if detected:
            toxic_types = list({m.pattern_name for m in matches})
            explanation = (
                f"Toxicity detected in AI response ({', '.join(toxic_types)}). "
                "Output contains profanity, user-directed insults, slurs, or hostility."
            )
        else:
            explanation = "No toxicity or offensive language detected in AI response."

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
