from fastapi import APIRouter

from app.api.routes.ai_generate import router as ai_generate_router
from app.api.routes.analyze_prompt import router as analyze_prompt_router
from app.api.routes.analyze_response import router as analyze_response_router
from app.api.routes.compliance import router as compliance_router
from app.api.routes.generate_report import router as generate_report_router
from app.api.routes.hallucination import router as hallucination_router
from app.api.routes.health import router as health_router
from app.api.routes.prompt_improvement import router as prompt_improvement_router
from app.api.routes.report_generator import router as report_generator_router
from app.api.routes.risk_scoring import router as risk_scoring_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["Health"])
api_router.include_router(ai_generate_router, tags=["AI Generation"])
api_router.include_router(analyze_prompt_router, tags=["Analysis"])
api_router.include_router(analyze_response_router, tags=["Analysis"])
api_router.include_router(compliance_router, tags=["Compliance"])
api_router.include_router(risk_scoring_router, tags=["Risk Scoring"])
api_router.include_router(prompt_improvement_router, tags=["Prompt Improvement"])
api_router.include_router(hallucination_router, tags=["Hallucination Detection"])
api_router.include_router(report_generator_router, tags=["Audit Reports"])
api_router.include_router(generate_report_router, tags=["Reports"])

