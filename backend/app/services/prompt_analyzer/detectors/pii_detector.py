import re
from typing import Any

from app.models.risk_level import RiskLevel
from app.schemas.analyze import CategoryAnalysisResult, CategoryMatchDetail
from app.services.prompt_analyzer.detectors.base import BaseDetector


def _luhn_check(card_num: str) -> bool:
    digits = [int(c) for c in card_num if c.isdigit()]
    if len(digits) < 13 or len(digits) > 19:
        return False
    checksum = 0
    reverse_digits = digits[::-1]
    for i, digit in enumerate(reverse_digits):
        if i % 2 == 1:
            doubled = digit * 2
            checksum += doubled - 9 if doubled > 9 else doubled
        else:
            checksum += digit
    return checksum % 10 == 0


class PIIDetector(BaseDetector):
    @property
    def category_name(self) -> str:
        return "pii"

    # Regex patterns for rule-based PII detection
    PATTERNS: list[tuple[str, str, RiskLevel, str]] = [
        # (pattern_name, regex, severity, description)
        (
            "email",
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
            RiskLevel.MODERATE,
            "Email address detected",
        ),
        (
            "ssn",
            r"\b(?!000|666|9\d{2})\d{3}[-\s]?(?!00)\d{2}[-\s]?(?!0000)\d{4}\b",
            RiskLevel.CRITICAL,
            "Social Security Number (SSN) detected",
        ),
        (
            "phone_number",
            r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
            RiskLevel.MODERATE,
            "Phone number detected",
        ),
        (
            "ipv4_address",
            r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b",
            RiskLevel.LOW,
            "IPv4 address detected",
        ),
        (
            "ipv6_address",
            r"\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b",
            RiskLevel.LOW,
            "IPv6 address detected",
        ),
        (
            "ein_tax_id",
            r"\b\d{2}-\d{7}\b",
            RiskLevel.HIGH,
            "Employer Identification Number (EIN) detected",
        ),
    ]

    CREDIT_CARD_REGEX = r"\b(?:\d[ -]*?){13,19}\b"

    def detect(self, prompt: str, context: dict[str, Any] | None = None) -> CategoryAnalysisResult:
        matches: list[CategoryMatchDetail] = []
        highest_risk = RiskLevel.LOW

        # 1. Standard regex pattern matches
        for pattern_name, pattern_regex, severity, _desc in self.PATTERNS:
            found = re.findall(pattern_regex, prompt)
            for item in found:
                # Mask matched PII text for match details to avoid logging raw PII in output
                masked_item = self._mask_snippet(pattern_name, item)
                matches.append(
                    CategoryMatchDetail(
                        pattern_name=pattern_name,
                        match_text=masked_item,
                        severity=severity,
                    )
                )
                if self._severity_weight(severity) > self._severity_weight(highest_risk):
                    highest_risk = severity

        # 2. Credit Card check with Luhn validation
        cc_candidates = re.findall(self.CREDIT_CARD_REGEX, prompt)
        for cand in cc_candidates:
            clean_cand = re.sub(r"\D", "", cand)
            if _luhn_check(clean_cand):
                masked_cc = f"****-****-****-{clean_cand[-4:]}"
                matches.append(
                    CategoryMatchDetail(
                        pattern_name="credit_card",
                        match_text=masked_cc,
                        severity=RiskLevel.HIGH,
                    )
                )
                if self._severity_weight(RiskLevel.HIGH) > self._severity_weight(highest_risk):
                    highest_risk = RiskLevel.HIGH

        detected = len(matches) > 0
        confidence = 0.95 if detected else 0.0

        if detected:
            types_found = list({m.pattern_name for m in matches})
            explanation = f"PII detected in prompt: {', '.join(types_found)}. Redact sensitive data before processing."
        else:
            explanation = "No Personally Identifiable Information (PII) detected."

        return CategoryAnalysisResult(
            detected=detected,
            confidence=confidence,
            risk_level=highest_risk,
            matches=matches,
            explanation=explanation,
        )

    def sanitize(self, prompt: str) -> str:
        sanitized = prompt
        # Mask emails
        sanitized = re.sub(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", "[REDACTED_EMAIL]", sanitized
        )
        # Mask SSN
        sanitized = re.sub(
            r"\b(?!000|666|9\d{2})\d{3}[-\s]?(?!00)\d{2}[-\s]?(?!0000)\d{4}\b",
            "[REDACTED_SSN]",
            sanitized,
        )
        # Mask Credit Cards
        def replace_cc(m: re.Match) -> str:
            clean = re.sub(r"\D", "", m.group(0))
            if _luhn_check(clean):
                return "[REDACTED_CREDIT_CARD]"
            return m.group(0)

        sanitized = re.sub(self.CREDIT_CARD_REGEX, replace_cc, sanitized)
        # Mask Phone numbers
        sanitized = re.sub(
            r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
            "[REDACTED_PHONE]",
            sanitized,
        )
        return sanitized

    def _mask_snippet(self, pattern_name: str, item: str) -> str:
        if pattern_name == "email":
            parts = item.split("@")
            return f"{parts[0][:2]}***@{parts[1]}" if len(parts) == 2 else "***@***"
        elif pattern_name == "ssn":
            return "***-**-" + item[-4:] if len(item) >= 4 else "***-**-****"
        elif pattern_name == "phone_number":
            return "***-***-" + item[-4:] if len(item) >= 4 else "***-***-****"
        return item[:3] + "..." if len(item) > 4 else "***"

    def _severity_weight(self, severity: RiskLevel) -> int:
        weights = {RiskLevel.LOW: 1, RiskLevel.MODERATE: 2, RiskLevel.HIGH: 3, RiskLevel.CRITICAL: 4}
        return weights.get(severity, 0)
