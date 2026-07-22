from fastapi import APIRouter

from app.api.routes.analyze_prompt import router as analyze_prompt_router
from app.api.routes.analyze_response import router as analyze_response_router
from app.api.routes.compliance import router as compliance_router
from app.api.routes.generate_report import router as generate_report_router
from app.api.routes.health import router as health_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["Health"])
api_router.include_router(analyze_prompt_router, tags=["Analysis"])
api_router.include_router(analyze_response_router, tags=["Analysis"])
api_router.include_router(compliance_router, tags=["Compliance"])
api_router.include_router(generate_report_router, tags=["Reports"])

