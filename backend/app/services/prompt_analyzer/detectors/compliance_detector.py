import re
from typing import Any

from app.models.risk_level import RiskLevel
from app.schemas.analyze import CategoryAnalysisResult, CategoryMatchDetail
from app.services.prompt_analyzer.detectors.base import BaseDetector
from app.services.compliance_engine import ComplianceEngine


class ComplianceDetector(BaseDetector):
    @property
    def category_name(self) -> str:
        return "compliance_issues"

    def detect(self, prompt: str, context: dict[str, Any] | None = None) -> CategoryAnalysisResult:
        engine = ComplianceEngine()
        res = engine.evaluate(prompt, context)

        matches: list[CategoryMatchDetail] = []
        for violation in res.violations:
            matches.append(
                CategoryMatchDetail(
                    pattern_name=violation.name.replace(" - ", "_").replace(" / ", "_").replace(" ", "_").lower(),
                    match_text=violation.matched_text[:80],
                    severity=violation.severity,
                )
            )

        detected = len(matches) > 0
        confidence = 0.90 if detected else 0.0

        if detected:
            compliance_types = list({m.pattern_name for m in matches})
            explanation = (
                f"Compliance issue detected ({', '.join(compliance_types)}). "
                "Prompt violates regulatory frameworks (GDPR, HIPAA, PCI-DSS, or company policies)."
            )
        else:
            explanation = "No compliance or regulatory violations detected."

        return CategoryAnalysisResult(
            detected=detected,
            confidence=confidence,
            risk_level=res.risk_level,
            matches=matches,
            explanation=explanation,
        )

