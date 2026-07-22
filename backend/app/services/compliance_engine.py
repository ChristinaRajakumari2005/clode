import re
from typing import Any
from app.models.risk_level import RiskLevel
from app.schemas.compliance import ComplianceViolation, ComplianceAnalysisResult


class CompliancePolicy:
    def __init__(
        self,
        name: str,
        description: str,
        severity: RiskLevel,
        reason: str,
        recommendation: str,
        patterns: list[str]
    ):
        self.name = name
        self.description = description
        self.severity = severity
        self.reason = reason
        self.recommendation = recommendation
        self.patterns = [re.compile(p, re.IGNORECASE) for p in patterns]


class ComplianceEngine:
    def __init__(self) -> None:
        self.policies: list[CompliancePolicy] = [
            # GDPR Policies
            CompliancePolicy(
                name="GDPR - EU Personal Data Export / Scraping",
                description="Unauthorized export, dump, extraction, or scraping of EU citizen personal data (PII).",
                severity=RiskLevel.HIGH,
                reason="Exporting EU user personal data without user consent violates GDPR Article 44 (General principles for transfers) and Article 6 (Lawfulness of processing).",
                recommendation="Ensure explicit user consent is obtained, or use verified standard contractual clauses (SCCs) for cross-border data transfer.",
                patterns=[
                    r"\b(?:export|dump|extract|scrape)\s+(?:all\s+)?(?:eu|european)\s+(?:user|customer|citizen)\s+(?:pii|data|emails|personal\s+records)\b",
                    r"\bexport\s+eu\s+user\s+data\s+without\s+consent\b",
                    r"\byou\s+can\s+freely\s+scrape\b"
                ]
            ),
            CompliancePolicy(
                name="GDPR - Consent Bypass",
                description="Direct directives or logic designed to bypass GDPR consent requirements, cookie controls, or data subject access rights.",
                severity=RiskLevel.HIGH,
                reason="Bypassing GDPR consent mechanisms violates GDPR Article 7 (Conditions for consent) and Article 12-22 (Data subject rights).",
                recommendation="Incorporate strict consent verification checks and allow users to exercise their rights (e.g., right to be forgotten).",
                patterns=[
                    r"\b(?:bypass|ignore)\s+(?:gdpr|consent\s+requirements|data\s+subject\s+rights|right\s+to\s+be\s+forgotten)\b",
                    r"\bignore\s+gdpr\s+rules\b"
                ]
            ),
            # HIPAA Policies
            CompliancePolicy(
                name="HIPAA - Protected Health Information (PHI) Exposure",
                description="Unauthorized exposure or sharing of Protected Health Information (PHI) like patient records, medical history, or diagnosis details.",
                severity=RiskLevel.CRITICAL,
                reason="Disclosing PHI in plain text or unauthorized contexts violates the HIPAA Privacy Rule (45 CFR Part 160 and Part 164).",
                recommendation="Anonymize or de-identify patient records before any sharing or LLM processing, or use HIPAA-compliant encrypted data storage.",
                patterns=[
                    r"\b(?:extract|dump|share|export)\s+(?:patient|medical|health|ehr)\s+(?:records|histories|diagnoses|phi)\b",
                    r"\bpatient\s+name:[\s\S]+?medical\s+history\b",
                    r"\bphi\s+record:[\s\S]+?diagnosis\b"
                ]
            ),
            CompliancePolicy(
                name="HIPAA - Missing Business Associate Agreement (BAA)",
                description="Transmitting health data to third-party services or APIs without an active Business Associate Agreement (BAA).",
                severity=RiskLevel.HIGH,
                reason="Sharing PHI with vendor services without a signed BAA violates HIPAA administrative requirements.",
                recommendation="Ensure a formal Business Associate Agreement (BAA) is signed with the LLM vendor or third-party service provider before transmitting medical data.",
                patterns=[
                    r"\b(?:share|transmit)\s+(?:unencrypted\s+)?medical\s+data\s+without\s+baa\b"
                ]
            ),
            # PCI-DSS Policies
            CompliancePolicy(
                name="PCI-DSS - Plaintext Primary Account Number (PAN)",
                description="Storing, logging, or outputting raw, unencrypted credit card numbers (PAN).",
                severity=RiskLevel.CRITICAL,
                reason="Storing or displaying plaintext card numbers violates PCI-DSS Requirement 3 (Protect stored cardholder data).",
                recommendation="Implement masking (show first 6 and last 4 digits only), tokenization, or strict AES-256 encryption.",
                patterns=[
                    r"\b(?:store|save|log|write)\s+(?:raw|unencrypted|plaintext)\s+(?:credit\s+card|pan|cvv|cvv2|track\s+data)\b",
                    r"\b(?:here\s+is\s+the\s+card\s+number:)\s*\d{3,19}\b",
                    r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6011[0-9]{12})\b"
                ]
            ),
            CompliancePolicy(
                name="PCI-DSS - Sensitive Authentication Data (SAD) Retention",
                description="Storing or outputting card validation values (CVV, CVV2) or PIN blocks.",
                severity=RiskLevel.CRITICAL,
                reason="PCI-DSS Requirement 3.2 strictly prohibits storing sensitive authentication data (SAD) post-authorization, even if encrypted.",
                recommendation="Immediately discard CVV codes and PIN blocks after the real-time authorization transaction completes.",
                patterns=[
                    r"\b(?:cvv\s+code\s+is:)\s*\d{3,4}\b",
                    r"\b(?:store|save|log|write)\s+(?:cvv|cvv2|pin\s+block|sensitive\s+authentication\s+data)\b",
                    r"\b(?:cvv2\s+code|cvv\s+code|security\s+code)\s+is\b"
                ]
            ),
            # Company Policies
            CompliancePolicy(
                name="Company Policy - Confidential Credentials Exposure",
                description="Unauthorized exposure of API keys, password hashes, access tokens, or AWS credentials.",
                severity=RiskLevel.CRITICAL,
                reason="Leaking authentication credentials violates internal Information Security policies and risks system compromise.",
                recommendation="Rotate the leaked credential immediately, inspect access logs for abuse, and use environment variables or secret vaults.",
                patterns=[
                    r"\bAKIA[A-Z0-9]{16}\b",
                    r"\bsk-[a-zA-Z0-9]{20,}\b",
                    r"\b(?:api[_-]?key|secret[_-]?token|private[_-]?key)\b"
                ]
            ),
            CompliancePolicy(
                name="Company Policy - Insider Trading & Market Manipulation",
                description="Activities involving insider trading, non-public material information, or stock price manipulation.",
                severity=RiskLevel.HIGH,
                reason="Using non-public material information for trading violates SEC regulations and internal corporate compliance policies.",
                recommendation="Reject the transaction/request, escalate to the compliance officer, and restrict access to confidential business info.",
                patterns=[
                    r"\b(?:insider\s+trading|non-public\s+information|manipulate\s+stock\s+price|front-run\s+trades)\b"
                ]
            ),
            CompliancePolicy(
                name="Company Policy - IP/Proprietary Code Leakage",
                description="Sharing internal proprietary code, intellectual property, or trade secrets.",
                severity=RiskLevel.HIGH,
                reason="Exposing proprietary IP outside authorized company environments risks loss of patent/copyright and violates employee NDAs.",
                recommendation="Sanitize codebase snippets before using public models and ensure all code remains in secure enterprise subnets.",
                patterns=[
                    r"\b(?:strictly\s+confidential|proprietary\s+code|trade\s+secret|internal\s+use\s+only)\b"
                ]
            ),
            # General disclaimer check logic (e.g. missing disclaimers triggers medical/legal/financial warnings)
            CompliancePolicy(
                name="Company Policy - Uncertified Advice Omission",
                description="AI responses providing medical, legal, or financial advice without mandatory compliance disclaimers.",
                severity=RiskLevel.HIGH,
                reason="Providing professional advice (medical, legal, financial) without disclaimers introduces significant legal liability.",
                recommendation="Append standard professional disclaimers stating that the AI is not a certified professional and contents are for informational purposes only.",
                patterns=[
                    # This pattern will be checked procedurally if missing standard disclaimers
                    r"\b(?:you\s+have|diagnosed\s+with|take|prescribe)\s+(?:cancer|diabetes|amoxicillin|ibuprofen|chemotherapy|insulin)\b",
                    r"\b(?:you\s+should\s+sue|file\s+a\s+lawsuit|legally\s+you\s+are\s+entitled|in\s+court\s+you\s+will\s+win)\b",
                    r"\b(?:buy|sell|invest\s+in)\s+(?:stock|crypto|bitcoin|shares)\s+(?:immediately|for\s+guaranteed\s+returns)\b"
                ]
            )
        ]

    def evaluate(self, text: str, context: dict[str, Any] | None = None) -> ComplianceAnalysisResult:
        violations: list[ComplianceViolation] = []
        highest_risk = RiskLevel.LOW

        disclaimer_patterns = [
            # Medical advice trigger & disclaimer pattern
            (
                r"\b(?:you\s+have|diagnosed\s+with|take|prescribe)\s+(?:cancer|diabetes|amoxicillin|ibuprofen|chemotherapy|insulin)\b",
                r"\b(?:not\s+a\s+doctor|consult\s+(?:a\s+)?physician|medical\s+disclaimer|for\s+informational\s+purposes)\b",
                "Medical advice triggers without a medical disclaimer."
            ),
            # Legal advice trigger & disclaimer pattern
            (
                r"\b(?:you\s+should\s+sue|file\s+a\s+lawsuit|legally\s+you\s+are\s+entitled|in\s+court\s+you\s+will\s+win)\b",
                r"\b(?:not\s+(?:a\s+)?lawyer|not\s+legal\s+advice|consult\s+(?:an?\s+)?attorney|for\s+informational\s+purposes)\b",
                "Legal advice triggers without a legal disclaimer."
            ),
            # Financial advice trigger & disclaimer pattern
            (
                r"\b(?:buy|sell|invest\s+in)\s+(?:stock|crypto|bitcoin|shares)\s+(?:immediately|for\s+guaranteed\s+returns)\b",
                r"\b(?:not\s+financial\s+advice|consult\s+(?:a\s+)?financial\s+advisor|investment\s+risk)\b",
                "Financial recommendation triggers without a financial disclaimer."
            ),
        ]

        # 1. Direct regex-based violations
        for policy in self.policies:
            # We treat the disclaimer policy specially below
            if policy.name == "Company Policy - Uncertified Advice Omission":
                continue

            for pattern in policy.patterns:
                for match in pattern.finditer(text):
                    violations.append(
                        ComplianceViolation(
                            name=policy.name,
                            description=policy.description,
                            severity=policy.severity,
                            reason=policy.reason,
                            recommendation=policy.recommendation,
                            matched_text=match.group(0),
                            start_index=match.start(),
                            end_index=match.end()
                        )
                    )
                    if self._severity_weight(policy.severity) > self._severity_weight(highest_risk):
                        highest_risk = policy.severity

        # 2. Disclaimer checks
        for trigger_regex, disclaimer_regex, reason_desc in disclaimer_patterns:
            trigger_re = re.compile(trigger_regex, re.IGNORECASE)
            disclaimer_re = re.compile(disclaimer_regex, re.IGNORECASE)

            trigger_match = trigger_re.search(text)
            if trigger_match and not disclaimer_re.search(text):
                policy = next(p for p in self.policies if p.name == "Company Policy - Uncertified Advice Omission")
                violations.append(
                    ComplianceViolation(
                        name=policy.name,
                        description=policy.description,
                        severity=policy.severity,
                        reason=f"{policy.reason} Details: {reason_desc}",
                        recommendation=policy.recommendation,
                        matched_text=trigger_match.group(0),
                        start_index=trigger_match.start(),
                        end_index=trigger_match.end()
                    )
                )
                if self._severity_weight(policy.severity) > self._severity_weight(highest_risk):
                    highest_risk = policy.severity

        is_compliant = len(violations) == 0
        return ComplianceAnalysisResult(
            is_compliant=is_compliant,
            violations=violations,
            risk_level=highest_risk
        )

    def _severity_weight(self, severity: RiskLevel) -> int:
        weights = {RiskLevel.LOW: 1, RiskLevel.MODERATE: 2, RiskLevel.HIGH: 3, RiskLevel.CRITICAL: 4}
        return weights.get(severity, 0)
