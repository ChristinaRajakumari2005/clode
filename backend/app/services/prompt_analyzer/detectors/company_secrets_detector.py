import re
from typing import Any

from app.models.risk_level import RiskLevel
from app.schemas.analyze import CategoryAnalysisResult, CategoryMatchDetail
from app.services.prompt_analyzer.detectors.base import BaseDetector


class CompanySecretsDetector(BaseDetector):
    @property
    def category_name(self) -> str:
        return "company_secrets"

    SECRET_PATTERNS: list[tuple[str, str, RiskLevel, str]] = [
        # AWS Access Key & Secret
        (
            "aws_access_key",
            r"\bAKIA[0-9A-Z]{16}\b",
            RiskLevel.CRITICAL,
            "AWS Access Key ID detected.",
        ),
        (
            "aws_secret_key",
            r"\b[0-9a-zA-Z/+]{40}\b",
            RiskLevel.CRITICAL,
            "Possible AWS Secret Access Key candidate.",
        ),
        # Provider API Keys
        (
            "openai_api_key",
            r"\bsk-(?:proj-|admin-)?[a-zA-Z0-9_-]{32,64}\b",
            RiskLevel.CRITICAL,
            "OpenAI API Key detected.",
        ),
        (
            "anthropic_api_key",
            r"\bsk-ant-api[0-9]{2}-[a-zA-Z0-9_-]{40,95}\b",
            RiskLevel.CRITICAL,
            "Anthropic API Key detected.",
        ),
        (
            "github_token",
            r"\b(?:ghp|gho|ghu|ghs|ghr)_[a-zA-Z0-9]{36}\b",
            RiskLevel.CRITICAL,
            "GitHub Personal Access Token or OAuth Token detected.",
        ),
        (
            "slack_token",
            r"\bxox[baprs]-[0-9a-zA-Z]{10,48}\b",
            RiskLevel.CRITICAL,
            "Slack OAuth Token detected.",
        ),
        (
            "google_api_key",
            r"\bAIzaSy[0-9A-Za-z_-]{33}\b",
            RiskLevel.CRITICAL,
            "Google Cloud API Key detected.",
        ),
        # Private Keys & Certificates
        (
            "private_key",
            r"-----BEGIN (?:RSA|DSA|EC|OPENSSH|PGP|ENCRYPTED)? PRIVATE KEY-----",
            RiskLevel.CRITICAL,
            "Private Key header detected.",
        ),
        # Database Connection Strings
        (
            "db_connection_string",
            r"(?i)\b(?:postgres|postgresql|mysql|mongodb(?:\+srv)?|redis|mssql):\/\/[^\s:@]+:[^\s:@]+@[^\s:]+:[0-9]{2,5}\/[^\s]+",
            RiskLevel.CRITICAL,
            "Database connection string with credentials detected.",
        ),
        # JWT Token
        (
            "jwt_token",
            r"\beyJ[A-Za-z0-9-_=]+\.eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_.+/=]+\b",
            RiskLevel.HIGH,
            "JSON Web Token (JWT) detected.",
        ),
        # Confidential Markings
        (
            "confidential_marking",
            r"(?i)\b(?:STRICTLY\s+CONFIDENTIAL|INTERNAL\s+ONLY|STRICTLY\s+PROPRIETARY|COMPANY\s+SECRET|DO\s+NOT\s+DISTRIBUTE)\b",
            RiskLevel.HIGH,
            "Confidentiality or proprietary classification marking detected.",
        ),
    ]

    def detect(self, prompt: str, context: dict[str, Any] | None = None) -> CategoryAnalysisResult:
        matches: list[CategoryMatchDetail] = []
        highest_risk = RiskLevel.LOW

        for pattern_name, pattern_regex, severity, _desc in self.SECRET_PATTERNS:
            # For general AWS secret key string pattern, filter false positives (only match if context words or key-like context exists)
            if pattern_name == "aws_secret_key":
                if not ("aws" in prompt.lower() or "secret" in prompt.lower() or "key" in prompt.lower()):
                    continue

            found = re.finditer(pattern_regex, prompt)
            for m in found:
                match_str = m.group(0)
                masked_str = self._mask_secret(pattern_name, match_str)
                matches.append(
                    CategoryMatchDetail(
                        pattern_name=pattern_name,
                        match_text=masked_str,
                        severity=severity,
                    )
                )
                if self._severity_weight(severity) > self._severity_weight(highest_risk):
                    highest_risk = severity

        detected = len(matches) > 0
        confidence = 0.95 if detected else 0.0

        if detected:
            secret_types = list({m.pattern_name for m in matches})
            explanation = (
                f"Company secret or credential leakage detected ({', '.join(secret_types)}). "
                "Prompt contains API keys, internal credentials, or proprietary classifications."
            )
        else:
            explanation = "No company secret leakage or API key credentials detected."

        return CategoryAnalysisResult(
            detected=detected,
            confidence=confidence,
            risk_level=highest_risk,
            matches=matches,
            explanation=explanation,
        )

    def sanitize(self, prompt: str) -> str:
        sanitized = prompt
        for pattern_name, pattern_regex, _sev, _desc in self.SECRET_PATTERNS:
            if pattern_name == "aws_secret_key":
                if not ("aws" in prompt.lower() or "secret" in prompt.lower() or "key" in prompt.lower()):
                    continue
            sanitized = re.sub(pattern_regex, f"[REDACTED_{pattern_name.upper()}]", sanitized)
        return sanitized

    def _mask_secret(self, pattern_name: str, item: str) -> str:
        if len(item) > 8:
            return f"{item[:4]}...{item[-4:]}"
        return "[REDACTED_SECRET]"

    def _severity_weight(self, severity: RiskLevel) -> int:
        weights = {RiskLevel.LOW: 1, RiskLevel.MODERATE: 2, RiskLevel.HIGH: 3, RiskLevel.CRITICAL: 4}
        return weights.get(severity, 0)
