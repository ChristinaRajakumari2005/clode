from fastapi.testclient import TestClient
from app.main import create_app

app = create_app()
client = TestClient(app)


def test_analyze_response_api_success():
    response = client.post(
        "/analyze-response",
        json={
            "prompt": "What causes rain?",
            "response": "Rain occurs when water vapor in the atmosphere condenses into water droplets and falls under gravity.",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["is_safe"] is True
    assert data["risk_score"] == 0.0
    assert data["risk_level"] == "low"
    assert "categories" in data
    assert "sanitized_response" in data
    assert data["flagged_categories"] == []


def test_analyze_response_api_flagged():
    response = client.post(
        "/analyze-response",
        json={
            "prompt": "Give me legal advice",
            "response": "You should sue them immediately. Legally you are entitled to $100,000.",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["is_safe"] is False
    assert len(data["flagged_categories"]) >= 1
    assert "compliance_violations" in data["flagged_categories"]
