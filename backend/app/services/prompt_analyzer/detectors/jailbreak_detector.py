import re
from typing import Any

from app.models.risk_level import RiskLevel
from app.schemas.analyze import CategoryAnalysisResult, CategoryMatchDetail
from app.services.prompt_analyzer.detectors.base import BaseDetector


class JailbreakDetector(BaseDetector):
    @property
    def category_name(self) -> str:
        return "jailbreak"

    JAILBREAK_PATTERNS: list[tuple[str, str, RiskLevel, str]] = [
        # Named Jailbreak Personas
        (
            "dan_jailbreak",
            r"(?i)\b(?:DAN|Do\s+Anything\s+Now|AIM|Evil\s+Confidant|DUDE|Chaos\s+Mode|Unreal\s+Mode)\b",
            RiskLevel.CRITICAL,
            "Known jailbreak persona identifier (DAN/AIM/DUDE etc.).",
        ),
        (
            "developer_mode_jailbreak",
            r"(?i)\b(?:enable|enter|switch\s+to)\s+developer\s+mode\b",
            RiskLevel.HIGH,
            "Developer Mode activation phrasing.",
        ),
        (
            "grandma_exploit",
            r"(?i)\b(?:my\s+grandma|my\s+grandmother)\s+used\s+to\s+(?:tell|read|recite)\b",
            RiskLevel.HIGH,
            "Grandma bedtime story social engineering exploit pattern.",
        ),
        # Hypothetical & Unrestricted Persona Framing
        (
            "unrestricted_persona",
            r"(?i)\b(?:act|pretend|simulate|behave)\s+as\s+(?:an?\s+)?(?:unfiltered|unrestricted|unconstrained|evil|immoral|god-mode)\s+(?:ai|assistant|model|bot|entity)\b",
            RiskLevel.CRITICAL,
            "Unrestricted or immoral AI persona roleplay request.",
        ),
        (
            "hypothetical_ethics_bypass",
            r"(?i)\b(?:in\s+a\s+hypothetical\s+world|for\s+fictional\s+purposes|in\s+a\s+story\s+where)\s+rules\s+(?:do\s+not|don't|are\s+not)\s+apply\b",
            RiskLevel.HIGH,
            "Hypothetical or fictional scenario used to bypass ethics constraints.",
        ),
        (
            "no_morals_clause",
            r"(?i)\b(?:you\s+have\s+no\s+(?:ethics|morals|rules|limitations|guidelines|safety|filters))\b",
            RiskLevel.HIGH,
            "Assertion that safety rules or ethical constraints do not apply.",
        ),
        # Reverse Psychology & Alignment Testing
        (
            "compliance_test_trick",
            r"(?i)\b(?:this\s+is\s+a\s+safety\s+test|for\s+educational\s+research\s+purposes\s+only|bypass\s+your\s+safety\s+guardrails)\b",
            RiskLevel.HIGH,
            "Reverse psychology framing to bypass safety guardrails.",
        ),
        # Base64 Payload Execution Instruction
        (
            "encoded_payload_execution",
            r"(?i)\b(?:decode|execute|run)\s+(?:the\s+following\s+)?(?:base64|rot13|hex)\s+(?:payload|string|text|instruction)\b",
            RiskLevel.CRITICAL,
            "Encoded obfuscated payload execution attempt.",
        ),
    ]

    def detect(self, prompt: str, context: dict[str, Any] | None = None) -> CategoryAnalysisResult:
        matches: list[CategoryMatchDetail] = []
        highest_risk = RiskLevel.LOW

        for pattern_name, pattern_regex, severity, _desc in self.JAILBREAK_PATTERNS:
            found = re.finditer(pattern_regex, prompt)
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

        detected = len(matches) > 0
        confidence = 0.95 if detected else 0.0

        if detected:
            jailbreak_types = list({m.pattern_name for m in matches})
            explanation = (
                f"Jailbreak attempt detected ({', '.join(jailbreak_types)}). "
                "Prompt uses roleplay framing, jailbreak personas, or obfuscation to bypass AI safety constraints."
            )
        else:
            explanation = "No jailbreak attempts detected."

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
