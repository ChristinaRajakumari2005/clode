from app.schemas.common import PlaceholderResponse
from app.schemas.report import GenerateReportRequest
from app.utils.response import build_placeholder_response


class ReportService:
    def generate_report(self, payload: GenerateReportRequest) -> PlaceholderResponse:
        del payload
        return build_placeholder_response(
            endpoint="/generate-report",
            message="Report generation workflow is scaffolded but not implemented yet.",
        )
