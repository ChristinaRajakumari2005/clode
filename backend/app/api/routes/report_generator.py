from fastapi import APIRouter, Depends, status

from app.schemas.report_generator import GenerateAuditReportRequest, GenerateAuditReportResponse
from app.services.report_generator_service import ReportGeneratorService

router = APIRouter()


def get_report_generator_service() -> ReportGeneratorService:
    return ReportGeneratorService()


@router.post(
    "/generate-audit-report",
    response_model=GenerateAuditReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate a consolidated AI Governance Audit Report",
    description="Combines findings from prompt analysis, response analysis, compliance evaluation, risk scoring, and hallucination detection into a single audit report.",
)
def generate_audit_report(
    payload: GenerateAuditReportRequest,
    service: ReportGeneratorService = Depends(get_report_generator_service),
) -> GenerateAuditReportResponse:
    return service.generate_report(payload)
