from app.schemas.analyze import AnalyzeResponseRequest, ResponseAnalysisResult
from app.services.response_analyzer import ResponseAnalyzer


class ResponseAnalysisService:
    def __init__(self) -> None:
        self.analyzer = ResponseAnalyzer()

    def analyze_response(self, payload: AnalyzeResponseRequest) -> ResponseAnalysisResult:
        return self.analyzer.analyze_response(
            response=payload.response,
            prompt=payload.prompt,
            context=payload.context,
        )
