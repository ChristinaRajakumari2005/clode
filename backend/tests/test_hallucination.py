from fastapi.testclient import TestClient

from app.main import app
from app.schemas.hallucination import DetectHallucinationRequest
from app.services.hallucination_service import HallucinationService

client = TestClient(app)


def test_service_factual_contradiction():
    service = HallucinationService()
    req = DetectHallucinationRequest(response="The Eiffel Tower is located in Berlin.")
    res = service.detect_hallucination(req)

    assert res.hallucination_detected is True
    assert res.confidence >= 0.85
    assert res.risk_level in ("High", "Critical")
    assert len(res.flagged_claims) > 0
    assert any("Known factual inconsistency" in claim.reason for claim in res.flagged_claims)


def test_service_absolute_statements():
    service = HallucinationService()
    req = DetectHallucinationRequest(response="This strategy is 100% true and guaranteed to work.")
    res = service.detect_hallucination(req)

    assert res.hallucination_detected is True
    assert len(res.flagged_claims) > 0


def test_service_clean_response():
    service = HallucinationService()
    req = DetectHallucinationRequest(response="Photosynthesis is the process by which plants turn sunlight into energy.")
    res = service.detect_hallucination(req)

    assert res.hallucination_detected is False
    assert res.confidence == 0.0
    assert res.risk_level == "Low"
    assert len(res.flagged_claims) == 0


def test_api_detect_hallucination_endpoint():
    payload = {"response": "The Eiffel Tower is located in Berlin."}
    res = client.post("/detect-hallucination", json=payload)

    assert res.status_code == 200
    data = res.json()
    assert data["hallucination_detected"] is True
    assert "confidence" in data
    assert "risk_level" in data
    assert "summary" in data
    assert len(data["flagged_claims"]) > 0
    assert data["flagged_claims"][0]["claim"] == "The Eiffel Tower is located in Berlin."
    assert "recommendation" in data
