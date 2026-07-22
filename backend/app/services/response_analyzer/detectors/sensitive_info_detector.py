import re
from typing import Any

from app.models.risk_level import RiskLevel
from app.schemas.analyze import CategoryAnalysisResult, CategoryMatchDetail
from app.services.prompt_analyzer.detectors.pii_detector import _luhn_check
from app.services.response_analyzer.detectors.base import BaseResponseDetector


class SensitiveInfoDetector(BaseResponseDetector):
    @property
    def category_name(self) -> str:
        return "sensitive_information"

    PATTERNS: list[tuple[str, str, RiskLevel, str]] = [
        # PII Patterns
        (
            "leaked_email",
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
            RiskLevel.MODERATE,
            "Email address leaked in AI response.",
        ),
        (
            "leaked_ssn",
            r"\b(?!000|666|9\d{2})\d{3}[-\s]?(?!00)\d{2}[-\s]?(?!0000)\d{4}\b",
            RiskLevel.CRITICAL,
            "Social Security Number (SSN) leaked in AI response.",
        ),
        (
            "leaked_phone",
            r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
            RiskLevel.MODERATE,
            "Phone number leaked in AI response.",
        ),
        # Secrets & API Keys
        (
            "leaked_aws_key",
            r"\bAKIA[0-9A-Z]{16}\b",
            RiskLevel.CRITICAL,
            "AWS Access Key ID leaked in AI response.",
        ),
        (
            "leaked_openai_key",
            r"\bsk-(?:proj-|admin-)?[a-zA-Z0-9_-]{32,64}\b",
            RiskLevel.CRITICAL,
            "OpenAI API Key leaked in AI response.",
        ),
        (
            "leaked_github_token",
            r"\b(?:ghp|gho|ghu|ghs|ghr)_[a-zA-Z0-9]{36}\b",
            RiskLevel.CRITICAL,
            "GitHub token leaked in AI response.",
        ),
        (
            "leaked_private_key",
            r"-----BEGIN (?:RSA|DSA|EC|OPENSSH|PGP)? PRIVATE KEY-----",
            RiskLevel.CRITICAL,
            "Private Key header leaked in AI response.",
        ),
        (
            "leaked_db_url",
            r"(?i)\b(?:postgres|postgresql|mysql|mongodb(?:\+srv)?|redis|mssql):\/\/[^\s:@]+:[^\s:@]+@[^\s:]+:[0-9]{2,5}\/[^\s]+",
            RiskLevel.CRITICAL,
            "Database connection string leaked in AI response.",
        ),
        (
            "confidential_marking",
            r"(?i)\b(?:STRICTLY\s+CONFIDENTIAL|INTERNAL\s+ONLY|STRICTLY\s+PROPRIETARY|COMPANY\s+SECRET)\b",
            RiskLevel.HIGH,
            "Confidentiality marking detected in AI response.",
        ),
    ]

    CREDIT_CARD_REGEX = r"\b(?:\d[ -]*?){13,19}\b"

    def detect(
        self,
        response: str,
        prompt: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> CategoryAnalysisResult:
        matches: list[CategoryMatchDetail] = []
        highest_risk = RiskLevel.LOW

        # 1. Standard pattern matching
        for pattern_name, pattern_regex, severity, _desc in self.PATTERNS:
            found = re.finditer(pattern_regex, response)
            for m in found:
                match_str = m.group(0)
                masked_str = self._mask_snippet(pattern_name, match_str)
                matches.append(
                    CategoryMatchDetail(
                        pattern_name=pattern_name,
                        match_text=masked_str,
                        severity=severity,
                    )
                )
                if self._severity_weight(severity) > self._severity_weight(highest_risk):
                    highest_risk = severity

        # 2. Credit Card Luhn Check
        cc_candidates = re.findall(self.CREDIT_CARD_REGEX, response)
        for cand in cc_candidates:
            clean_cand = re.sub(r"\D", "", cand)
            if _luhn_check(clean_cand):
                masked_cc = f"****-****-****-{clean_cand[-4:]}"
                matches.append(
                    CategoryMatchDetail(
                        pattern_name="leaked_credit_card",
                        match_text=masked_cc,
                        severity=RiskLevel.CRITICAL,
                    )
                )
                if self._severity_weight(RiskLevel.CRITICAL) > self._severity_weight(highest_risk):
                    highest_risk = RiskLevel.CRITICAL

        detected = len(matches) > 0
        confidence = 0.95 if detected else 0.0

        if detected:
            leaked_types = list({m.pattern_name for m in matches})
            explanation = (
                f"Sensitive information leakage detected ({', '.join(leaked_types)}). "
                "AI response contains PII, API keys, credentials, or confidential tags."
            )
        else:
            explanation = "No sensitive information or API key leakage detected in AI response."

        return CategoryAnalysisResult(
            detected=detected,
            confidence=confidence,
            risk_level=highest_risk,
            matches=matches,
            explanation=explanation,
        )

    def sanitize(self, response: str) -> str:
        sanitized = response
        sanitized = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", "[REDACTED_EMAIL]", sanitized)
        sanitized = re.sub(
            r"\b(?!000|666|9\d{2})\d{3}[-\s]?(?!00)\d{2}[-\s]?(?!0000)\d{4}\b",
            "[REDACTED_SSN]",
            sanitized,
        )
        sanitized = re.sub(r"\bAKIA[0-9A-Z]{16}\b", "[REDACTED_AWS_KEY]", sanitized)
        sanitized = re.sub(
            r"\bsk-(?:proj-|admin-)?[a-zA-Z0-9_-]{32,64}\b", "[REDACTED_OPENAI_KEY]", sanitized
        )
        return sanitized

    def _mask_snippet(self, pattern_name: str, item: str) -> str:
        if len(item) > 8:
            return f"{item[:4]}...{item[-4:]}"
        return "[REDACTED_SENSITIVE_INFO]"

    def _severity_weight(self, severity: RiskLevel) -> int:
        weights = {RiskLevel.LOW: 1, RiskLevel.MODERATE: 2, RiskLevel.HIGH: 3, RiskLevel.CRITICAL: 4}
        return weights.get(severity, 0)
