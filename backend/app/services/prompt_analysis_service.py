from app.schemas.analyze import AnalyzePromptRequest, PromptAnalysisResult
from app.services.prompt_analyzer import PromptAnalyzer


class PromptAnalysisService:
    def __init__(self) -> None:
        self.analyzer = PromptAnalyzer()

    def analyze_prompt(self, payload: AnalyzePromptRequest) -> PromptAnalysisResult:
        return self.analyzer.analyze_prompt(prompt=payload.prompt, context=payload.context)
