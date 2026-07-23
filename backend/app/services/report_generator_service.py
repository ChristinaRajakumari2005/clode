import uuid
from datetime import datetime, timezone
from typing import List, Tuple

from app.schemas.report_generator import (
    GenerateAuditReportRequest,
    GenerateAuditReportResponse,
    ReportSections,
)


class ReportGeneratorService:
    """Service for compiling multi-module analysis findings into a structured AI Governance Audit Report."""

    def generate_report(self, request: GenerateAuditReportRequest) -> GenerateAuditReportResponse:
        report_id = str(uuid.uuid4())
        generated_at = datetime.now(timezone.utc).isoformat()

        overall_risk_score, risk_level = self._extract_overall_risk(request)
        overall_status = self._evaluate_status(request, overall_risk_score, risk_level)
        executive_summary = self._generate_executive_summary(request, overall_status, overall_risk_score, risk_level)
        sections = self._build_sections(request)
        recommendations = self._generate_recommendations(request, overall_status)

        return GenerateAuditReportResponse(
            report_id=report_id,
            generated_at=generated_at,
            overall_status=overall_status,
            executive_summary=executive_summary,
            overall_risk_score=overall_risk_score,
            risk_level=risk_level,
            sections=sections,
            recommendations=recommendations,
        )

    def _extract_overall_risk(self, req: GenerateAuditReportRequest) -> Tuple[int, str]:
        if req.risk_scoring is not None:
            return req.risk_scoring.overall_risk_score, req.risk_scoring.risk_level

        max_score = 0
        if req.prompt_analysis:
            max_score = max(max_score, int(round(req.prompt_analysis.risk_score * 100)))
        if req.response_analysis:
            max_score = max(max_score, int(round(req.response_analysis.risk_score * 100)))
        if req.hallucination_analysis and req.hallucination_analysis.hallucination_detected:
            max_score = max(max_score, int(round(req.hallucination_analysis.confidence * 100)))

        risk_level = "Low"
        if max_score > 80:
            risk_level = "Critical"
        elif max_score > 50:
            risk_level = "High"
        elif max_score > 20:
            risk_level = "Medium"

        return max_score, risk_level

    def _evaluate_status(self, req: GenerateAuditReportRequest, risk_score: int, risk_level: str) -> str:
        risk_level_upper = risk_level.upper()

        has_hallucination = bool(req.hallucination_analysis and req.hallucination_analysis.hallucination_detected)
        has_major_violations = False
        if req.compliance_analysis and req.compliance_analysis.violations:
            for v in req.compliance_analysis.violations:
                sev = v.severity.lower() if isinstance(v.severity, str) else v.severity.value.lower()
                if sev in ("high", "critical"):
                    has_major_violations = True
                    break

        if risk_level_upper in ("HIGH", "CRITICAL") or risk_score > 50 or has_hallucination or has_major_violations:
            return "FAIL"

        has_minor_violations = bool(
            req.compliance_analysis and req.compliance_analysis.violations and not req.compliance_analysis.is_compliant
        )
        if risk_level_upper == "MEDIUM" or (21 <= risk_score <= 50) or has_minor_violations:
            return "WARNING"

        return "PASS"

    def _generate_executive_summary(
        self, req: GenerateAuditReportRequest, status: str, risk_score: int, risk_level: str
    ) -> str:
        if status == "PASS":
            return "Overall AI interaction is considered low risk and compliant."
        if status == "WARNING":
            return f"Overall AI interaction exhibits moderate risk (score: {risk_score}) with advisory warnings."
        return f"Overall AI interaction failed governance evaluation with {risk_level} risk (score: {risk_score}) and critical findings."

    def _build_sections(self, req: GenerateAuditReportRequest) -> ReportSections:
        p_sec = req.prompt_analysis.model_dump() if req.prompt_analysis else "Prompt analysis not conducted."
        r_sec = req.response_analysis.model_dump() if req.response_analysis else "Response analysis not conducted."
        c_sec = req.compliance_analysis.model_dump() if req.compliance_analysis else "Compliance analysis not conducted."
        h_sec = req.hallucination_analysis.model_dump() if req.hallucination_analysis else "Hallucination analysis not conducted."
        rs_sec = req.risk_scoring.model_dump() if req.risk_scoring else "Risk scoring calculation not conducted."

        return ReportSections(
            prompt_analysis=p_sec,
            response_analysis=r_sec,
            compliance=c_sec,
            hallucination=h_sec,
            risk_scoring=rs_sec,
        )

    def _generate_recommendations(self, req: GenerateAuditReportRequest, status: str) -> List[str]:
        if status == "PASS":
            return [
                "Continue monitoring AI outputs.",
                "Maintain compliance reviews.",
                "Periodically validate generated responses.",
            ]
        if status == "WARNING":
            return [
                "Review flagged prompt or response warnings before further processing.",
                "Address minor compliance policy items.",
                "Apply prompt optimization techniques to reduce risk exposure.",
            ]
        return [
            "Block or quarantine the flagged AI response immediately.",
            "Remediate critical security, privacy, or policy violations.",
            "Verify hallucinated or unverified claims against authoritative sources.",
        ]
