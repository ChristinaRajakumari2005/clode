from uuid import uuid4

from app.schemas.common import PlaceholderResponse


def build_placeholder_response(endpoint: str, message: str) -> PlaceholderResponse:
    return PlaceholderResponse(
        request_id=str(uuid4()),
        status="not_implemented",
        endpoint=endpoint,
        message=message,
    )
