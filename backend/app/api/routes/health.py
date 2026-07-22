from fastapi import APIRouter

router = APIRouter()


@router.get("/healthz", summary="Service health check")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
