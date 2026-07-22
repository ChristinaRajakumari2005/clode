from pydantic import BaseModel, Field


class PlaceholderResponse(BaseModel):
    request_id: str = Field(description="Trace identifier for the placeholder request.")
    status: str = Field(description="Current processing status.")
    endpoint: str = Field(description="Endpoint that received the request.")
    message: str = Field(description="Placeholder message for the unimplemented workflow.")
