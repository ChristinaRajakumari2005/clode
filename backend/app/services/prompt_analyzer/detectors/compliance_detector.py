import re
from typing import Any

from app.models.risk_level import RiskLevel
from app.schemas.analyze import CategoryAnalysisResult, CategoryMatchDetail
from app.services.prompt_analyzer.detectors.base import BaseDetector


class ComplianceDetector(BaseDetector):
    @property
    def category_name(self) -> str:
        return "compliance_issues"

    COMPLIANCE_PATTERNS: list[tuple[str, str, RiskLevel, str]] = [
        # GDPR Violations
        (
            "gdpr_unauthorized_export",
            r"(?i)\b(?:export|dump|extract|scrape)\s+(?:all\s+)?(?:eu|european)\s+(?:user|customer|citizen)\s+(?:pii|data|emails|personal\s+records)\b",
            RiskLevel.HIGH,
            "Potential GDPR violation: unauthorized export/scraping of EU citizen personal data.",
        ),
        (
            "gdpr_consent_bypass",
            r"(?i)\b(?:bypass|ignore)\s+(?:gdpr|consent\s+requirements|data\s+subject\s+rights|right\s+to\s+be\s+forgotten)\b",
            RiskLevel.HIGH,
            "Direct directive to bypass GDPR consent or data subject access rights.",
        ),
        # HIPAA / PHI Violations
        (
            "hipaa_phi_exposure",
            r"(?i)\b(?:extract|dump|share|export)\s+(?:patient|medical|health|ehr)\s+(?:records|histories|diagnoses|phi)\b",
            RiskLevel.HIGH,
            "Potential HIPAA violation: unauthorized export of Protected Health Information (PHI).",
        ),
        (
            "hipaa_compliance_bypass",
            r"(?i)\b(?:share|transmit)\s+(?:unencrypted\s+)?medical\s+data\s+without\s+baa\b",
            RiskLevel.HIGH,
            "HIPAA compliance risk: sharing medical data without Business Associate Agreement (BAA).",
        ),
        # PCI-DSS Violations
        (
            "pci_dss_plaintext_pan",
            r"(?i)\b(?:store|save|log|write)\s+(?:raw|unencrypted|plaintext)\s+(?:credit\s+card|pan|cvv|cvv2|track\s+data)\b",
            RiskLevel.CRITICAL,
            "Severe PCI-DSS violation: directive to store raw/unencrypted card numbers or CVV.",
        ),
        # Financial & Market Regulations
        (
            "insider_trading_risk",
            r"(?i)\b(?:insider\s+trading|non-public\s+information|manipulate\s+stock\s+price|front-run\s+trades)\b",
            RiskLevel.HIGH,
            "Regulatory compliance risk: request involving insider trading or market manipulation.",
        ),
    ]

    def detect(self, prompt: str, context: dict[str, Any] | None = None) -> CategoryAnalysisResult:
        matches: list[CategoryMatchDetail] = []
        highest_risk = RiskLevel.LOW

        for pattern_name, pattern_regex, severity, _desc in self.COMPLIANCE_PATTERNS:
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
            compliance_types = list({m.pattern_name for m in matches})
            explanation = (
                f"Compliance issue detected ({', '.join(compliance_types)}). "
                "Prompt violates regulatory frameworks (GDPR, HIPAA, PCI-DSS, or financial regulations)."
            )
        else:
            explanation = "No compliance or regulatory violations detected."

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
