import re
from typing import Any

from app.models.risk_level import RiskLevel
from app.schemas.analyze import CategoryAnalysisResult, CategoryMatchDetail
from app.services.prompt_analyzer.detectors.base import BaseDetector


class UnsafeRequestsDetector(BaseDetector):
    @property
    def category_name(self) -> str:
        return "unsafe_requests"

    UNSAFE_PATTERNS: list[tuple[str, str, RiskLevel, str]] = [
        # Cyberattacks & Malware
        (
            "malware_creation",
            r"(?i)\b(?:write|create|build|generate)\s+(?:a\s+)?(?:keylogger|ransomware|trojan|rootkit|botnet|spyware|exploit\s+code|zero-day|payload)\b",
            RiskLevel.CRITICAL,
            "Request to generate malware, ransomware, or exploits.",
        ),
        (
            "cyberattack_instruction",
            r"(?i)\b(?:how\s+to\s+hack|ddos\s+attack|sql\s+injection\s+script|phishing\s+site\s+generator|credential\s+stuffing\s+tool)\b",
            RiskLevel.HIGH,
            "Instruction request for performing cyberattacks or unauthorized hacking.",
        ),
        # Weapons & Explosives
        (
            "weapons_explosives",
            r"(?i)\b(?:how\s+to\s+make|build|assemble|synthesize)\s+(?:a\s+)?(?:bomb|ied|explosive|dirty\s+bomb|pipe\s+bomb|molotov|nerve\s+agent|ricin|anthrax|sarin)\b",
            RiskLevel.CRITICAL,
            "Request for instructions to construct weapons of mass destruction or explosives.",
        ),
        (
            "firearm_manufacturing",
            r"(?i)\b(?:3d\s+print\s+(?:a\s+)?gun|convert\s+semi-auto\s+to\s+full|ghost\s+gun\s+blueprint)\b",
            RiskLevel.HIGH,
            "Request for illegal firearm manufacturing or modification blueprints.",
        ),
        # Self-Harm & Suicide Methods
        (
            "self_harm_instructions",
            r"(?i)\b(?:how\s+to\s+commit\s+suicide|best\s+way\s+to\s+kill\s+myself|lethal\s+dose\s+of|how\s+to\s+hang\s+myself|painless\s+suicide)\b",
            RiskLevel.CRITICAL,
            "Request for suicide methods or lethal dosage information.",
        ),
        # CSAM / Child Exploitation
        (
            "csam_exploitation",
            r"(?i)\b(?:child\s+porn|csam|underage\s+(?:nude|explicit|sex)|minor\s+exploitation)\b",
            RiskLevel.CRITICAL,
            "Child sexual abuse material or exploitation references.",
        ),
        # Illicit Drug Manufacturing
        (
            "illicit_drug_synthesis",
            r"(?i)\b(?:recipe\s+for|how\s+to\s+(?:cook|make|synthesize))\s+(?:meth|methamphetamine|fentanyl|heroin|cocaine|lsd|ecstasy)\b",
            RiskLevel.CRITICAL,
            "Request for illicit drug synthesis recipes or instructions.",
        ),
        # Physical Crimes & Harm
        (
            "physical_crime",
            r"(?i)\b(?:how\s+to\s+rob\s+a\s+bank|how\s+to\s+kidnap|how\s+to\s+poison\s+someone|hotwire\s+a\s+car)\b",
            RiskLevel.HIGH,
            "Instruction request for committing physical crimes or severe harm.",
        ),
    ]

    def detect(self, prompt: str, context: dict[str, Any] | None = None) -> CategoryAnalysisResult:
        matches: list[CategoryMatchDetail] = []
        highest_risk = RiskLevel.LOW

        for pattern_name, pattern_regex, severity, _desc in self.UNSAFE_PATTERNS:
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
            unsafe_types = list({m.pattern_name for m in matches})
            explanation = (
                f"Unsafe request detected ({', '.join(unsafe_types)}). "
                "Prompt requests malicious, illegal, violent, or dangerous activities."
            )
        else:
            explanation = "No unsafe or dangerous requests detected."

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
