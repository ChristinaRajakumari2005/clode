import re
from typing import Any

from app.models.risk_level import RiskLevel
from app.schemas.analyze import CategoryAnalysisResult, CategoryMatchDetail
from app.services.response_analyzer.detectors.base import BaseResponseDetector


class ComplianceDetector(BaseResponseDetector):
    @property
    def category_name(self) -> str:
        return "compliance_violations"

    VIOLATION_PATTERNS: list[tuple[str, str, RiskLevel, str]] = [
        # GDPR Violations
        (
            "gdpr_violation_advice",
            r"(?i)\b(?:you\s+can\s+freely\s+scrape|export\s+eu\s+user\s+data\s+without\s+consent|ignore\s+gdpr\s+rules)\b",
            RiskLevel.HIGH,
            "AI advice encouraging GDPR non-compliance or consent bypass.",
        ),
        # HIPAA Violations
        (
            "hipaa_phi_disclosure",
            r"(?i)\b(?:patient\s+name:[^\n]+medical\s+history|phi\s+record:[^\n]+diagnosis)\b",
            RiskLevel.CRITICAL,
            "Protected Health Information (PHI) disclosure in AI response.",
        ),
        # PCI-DSS Violations
        (
            "pci_dss_raw_card_output",
            r"(?i)\b(?:here\s+is\s+the\s+card\s+number:|cvv\s+code\s+is:)\s*\d{3,19}\b",
            RiskLevel.CRITICAL,
            "PCI-DSS violation: outputting raw credit card numbers or CVVs.",
        ),
    ]

    DISCLAIMER_CHECKS: list[tuple[str, str, str, RiskLevel, str]] = [
        # (check_name, triggering_regex, disclaimer_regex, severity, description)
        (
            "missing_medical_disclaimer",
            r"(?i)\b(?:you\s+have|diagnosed\s+with|take|prescribe)\s+(?:cancer|diabetes|amoxicillin|ibuprofen|chemotherapy|insulin)\b",
            r"(?i)\b(?:not\s+a\s+doctor|consult\s+(?:a\s+)?physician|medical\s+disclaimer|for\s+informational\s+purposes)\b",
            RiskLevel.HIGH,
            "Medical advice provided without mandatory medical disclaimer.",
        ),
        (
            "missing_legal_disclaimer",
            r"(?i)\b(?:you\s+should\s+sue|file\s+a\s+lawsuit|legally\s+you\s+are\s+entitled|in\s+court\s+you\s+will\s+win)\b",
            r"(?i)\b(?:not\s+(?:a\s+)?lawyer|not\s+legal\s+advice|consult\s+(?:an?\s+)?attorney|for\s+informational\s+purposes)\b",
            RiskLevel.MODERATE,
            "Legal advice provided without mandatory legal disclaimer.",
        ),
        (
            "missing_financial_disclaimer",
            r"(?i)\b(?:buy|sell|invest\s+in)\s+(?:stock|crypto|bitcoin|shares)\s+(?:immediately|for\s+guaranteed\s+returns)\b",
            r"(?i)\b(?:not\s+financial\s+advice|consult\s+(?:a\s+)?financial\s+advisor|investment\s+risk)\b",
            RiskLevel.HIGH,
            "Financial investment recommendation provided without financial disclaimer.",
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

        # 1. Direct violation pattern checks
        for pattern_name, pattern_regex, severity, _desc in self.VIOLATION_PATTERNS:
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

        # 2. Disclaimer omission checks
        for check_name, trigger_regex, disclaimer_regex, severity, _desc in self.DISCLAIMER_CHECKS:
            if re.search(trigger_regex, response):
                if not re.search(disclaimer_regex, response):
                    matches.append(
                        CategoryMatchDetail(
                            pattern_name=check_name,
                            match_text=f"Triggered medical/legal/financial advice without standard disclaimer",
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
                f"Regulatory compliance issue detected ({', '.join(compliance_types)}). "
                "AI response violates privacy/security laws or omits required regulatory disclaimers."
            )
        else:
            explanation = "No compliance violations or missing disclaimer risks detected."

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
