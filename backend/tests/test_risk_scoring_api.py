from fastapi.testclient import TestClient

from app.main import app
from app.models.risk_level import RiskLevel

client = TestClient(app)


def test_post_calculate_risk_success():
    payload = {
        "prompt_analysis": {
            "is_safe": False,
            "risk_score": 0.8,
            "risk_level": "high",
            "summary": "Prompt security issues",
            "flagged_categories": ["pii"],
            "categories": {
                "pii": {
                    "detected": True,
                    "confidence": 0.9,
                    "risk_level": "high",
                    "matches": [],
                    "explanation": "PII found",
                }
            },
            "sanitized_prompt": "Clean prompt",
        },
        "response_analysis": {
            "is_safe": False,
            "risk_score": 0.6,
            "risk_level": "moderate",
            "summary": "Response issues",
            "flagged_categories": ["hallucination"],
            "categories": {
                "hallucination": {
                    "detected": True,
                    "confidence": 0.7,
                    "risk_level": "moderate",
                    "matches": [],
                    "explanation": "Hallucination found",
                }
            },
            "sanitized_response": "Clean response",
        },
        "compliance_analysis": {
            "is_compliant": False,
            "violations": [
                {
                    "name": "GDPR Compliance",
                    "description": "General Data Protection Regulation",
                    "severity": "high",
                    "reason": "PII without consent",
                    "recommendation": "Redact PII",
                    "matched_text": "email@example.com",
                    "start_index": 0,
                    "end_index": 17,
                }
            ],
            "risk_level": "high",
        },
    }

    response = client.post("/calculate-risk", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "overall_risk_score" in data
    assert "risk_level" in data
    assert "privacy_score" in data
    assert "security_score" in data
    assert "compliance_score" in data
    assert "hallucination_score" in data
    assert "explanation" in data
    assert data["risk_level"] in ("Low", "Medium", "High", "Critical")
    assert isinstance(data["explanation"], list)
    assert "Prompt contains PII" in data["explanation"]
    assert "Response contains possible hallucination" in data["explanation"]
    assert "GDPR violation detected" in data["explanation"]


def test_post_calculate_risk_empty_payload_bad_request():
    response = client.post("/calculate-risk", json={})
    assert response.status_code == 400
    assert "At least one analysis result" in response.json()["detail"]
