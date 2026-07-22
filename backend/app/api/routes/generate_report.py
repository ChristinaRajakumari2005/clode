from fastapi import APIRouter, status

from app.schemas.common import PlaceholderResponse
from app.schemas.report import GenerateReportRequest
from app.services.report_service import ReportService

router = APIRouter()


@router.post(
    "/generate-report",
    response_model=PlaceholderResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Generate a governance and compliance audit report",
)
def generate_report(payload: GenerateReportRequest) -> PlaceholderResponse:
    service = ReportService()
    return service.generate_report(payload)
