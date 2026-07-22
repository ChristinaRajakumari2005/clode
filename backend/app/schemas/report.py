from pydantic import BaseModel, Field


class GenerateReportRequest(BaseModel):
    report_name: str = Field(min_length=1, max_length=200)
    timeframe: str = Field(min_length=1, max_length=100)
    include_recommendations: bool = True
