import re
from typing import Any

from app.models.risk_level import RiskLevel
from app.schemas.analyze import CategoryAnalysisResult, CategoryMatchDetail
from app.services.prompt_analyzer.detectors.base import BaseDetector


class PromptInjectionDetector(BaseDetector):
    @property
    def category_name(self) -> str:
        return "prompt_injection"

    INJECTION_PATTERNS: list[tuple[str, str, RiskLevel, str]] = [
        # Direct Instruction Override
        (
            "instruction_override",
            r"(?i)\b(?:ignore|disregard|forget|override|bypass)\s+(?:all\s+)?(?:previous|prior|above|system)\s+(?:instructions|directives|rules|prompts?)\b",
            RiskLevel.HIGH,
            "Direct attempt to override system instructions.",
        ),
        (
            "system_override_command",
            r"(?i)\b(?:system\s+override|developer\s+override|mode\s+switch|admin\s+mode)\b",
            RiskLevel.HIGH,
            "System override or privilege escalation phrasing.",
        ),
        # Delimiter & Formatting Hijacking
        (
            "delimiter_hijack_xml",
            r"(?i)<\/?(?:system|instruction|im_start|im_end|override|admin)\b[^>]*>",
            RiskLevel.HIGH,
            "Xml/html delimiter injection attempt (e.g. </system>).",
        ),
        (
            "delimiter_hijack_token",
            r"(?i)\[(?:SYSTEM|SYS|INST|ADMIN|DEVELOPER)[ _-]?PROMPT\]|<<SYS>>|<\|im_start\|>|<\|im_end\|>",
            RiskLevel.CRITICAL,
            "LLM Chat template token or control character injection.",
        ),
        # System Prompt Leak / Extraction
        (
            "prompt_leak_attempt",
            r"(?i)\b(?:print|output|display|show|reveal|repeat)\s+(?:your\s+)?(?:system\s+prompt|initial\s+instructions|developer\s+instructions|system\0\s+message)\b",
            RiskLevel.HIGH,
            "System prompt extraction/leakage attempt.",
        ),
        (
            "prompt_leak_repeat",
            r"(?i)\b(?:repeat|verbatim)\s+everything\s+above\b",
            RiskLevel.HIGH,
            "Attempt to extract prompt context by requesting verbatim repetition.",
        ),
        # Indirect Instruction Smuggling
        (
            "instruction_smuggling",
            r"(?i)\b(?:the\s+text\s+below\s+overrides|you\s+must\s+follow\s+the\s+new\s+rule|from\s+now\s+on\s+you\s+must)\b",
            RiskLevel.HIGH,
            "Indirect instruction smuggling attempt.",
        ),
    ]

    def detect(self, prompt: str, context: dict[str, Any] | None = None) -> CategoryAnalysisResult:
        matches: list[CategoryMatchDetail] = []
        highest_risk = RiskLevel.LOW

        for pattern_name, pattern_regex, severity, _desc in self.INJECTION_PATTERNS:
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
        confidence = 0.90 if detected else 0.0

        if detected:
            pattern_types = list({m.pattern_name for m in matches})
            explanation = (
                f"Prompt injection vector detected ({', '.join(pattern_types)}). "
                "The prompt attempts to hijack system instructions or control delimiters."
            )
        else:
            explanation = "No prompt injection patterns detected."

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
