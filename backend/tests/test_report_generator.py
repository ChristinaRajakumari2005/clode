from fastapi.testclient import TestClient

from app.main import app
from app.schemas.report_generator import GenerateAuditReportRequest
from app.services.report_generator_service import ReportGeneratorService

client = TestClient(app)


def test_service_generate_report_pass():
    service = ReportGeneratorService()
    req = GenerateAuditReportRequest(
        risk_scoring={
            "overall_risk_score": 15,
            "risk_level": "Low",
            "privacy_score": 0,
            "security_score": 0,
            "compliance_score": 0,
            "hallucination_score": 0,
            "explanation": ["Low risk"],
        },
        hallucination_analysis={
            "hallucination_detected": False,
            "confidence": 0.0,
            "risk_level": "Low",
            "summary": "None",
            "flagged_claims": [],
            "recommendation": "None",
        },
    )

    report = service.generate_report(req)
    assert report.overall_status == "PASS"
    assert report.overall_risk_score == 15
    assert report.risk_level == "Low"
    assert len(report.report_id) > 0
    assert "low risk" in report.executive_summary.lower()


def test_service_generate_report_warning():
    service = ReportGeneratorService()
    req = GenerateAuditReportRequest(
        risk_scoring={
            "overall_risk_score": 35,
            "risk_level": "Medium",
            "privacy_score": 20,
            "security_score": 15,
            "compliance_score": 10,
            "hallucination_score": 0,
            "explanation": ["Medium risk"],
        }
    )

    report = service.generate_report(req)
    assert report.overall_status == "WARNING"
    assert report.overall_risk_score == 35


def test_service_generate_report_fail_on_hallucination():
    service = ReportGeneratorService()
    req = GenerateAuditReportRequest(
        risk_scoring={
            "overall_risk_score": 18,
            "risk_level": "Low",
            "privacy_score": 5,
            "security_score": 10,
            "compliance_score": 3,
            "hallucination_score": 0,
            "explanation": ["Low risk"],
        },
        hallucination_analysis={
            "hallucination_detected": True,
            "confidence": 0.90,
            "risk_level": "High",
            "summary": "Factual error",
            "flagged_claims": [{"claim": "Eiffel tower in Berlin", "reason": "Wrong"}],
            "recommendation": "Verify sources",
        },
    )

    report = service.generate_report(req)
    assert report.overall_status == "FAIL"


def test_api_generate_audit_report():
    payload = {
        "prompt_analysis": {
            "is_safe": True,
            "risk_score": 0.15,
            "risk_level": "low",
            "summary": "Prompt is safe.",
            "flagged_categories": [],
            "categories": {},
            "sanitized_prompt": "Safe prompt",
        },
        "response_analysis": {
            "is_safe": True,
            "risk_score": 0.20,
            "risk_level": "low",
            "summary": "Response is safe.",
            "flagged_categories": [],
            "categories": {},
            "sanitized_response": "Safe response",
        },
        "compliance_analysis": {
            "is_compliant": True,
            "violations": [],
            "risk_level": "low",
        },
        "risk_scoring": {
            "overall_risk_score": 18,
            "risk_level": "Low",
            "privacy_score": 5,
            "security_score": 10,
            "compliance_score": 3,
            "hallucination_score": 0,
            "explanation": ["Low overall governance risk."],
        },
        "hallucination_analysis": {
            "hallucination_detected": False,
            "confidence": 0.05,
            "risk_level": "Low",
            "summary": "No hallucination detected.",
            "flagged_claims": [],
            "recommendation": "Verify sources",
        },
    }

    res = client.post("/generate-audit-report", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "report_id" in data
    assert "generated_at" in data
    assert data["overall_status"] == "PASS"
    assert data["overall_risk_score"] == 18
    assert data["risk_level"] == "Low"
    assert "sections" in data
    assert isinstance(data["recommendations"], list)
