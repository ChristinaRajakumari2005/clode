from fastapi.testclient import TestClient
from app.main import create_app

app = create_app()
client = TestClient(app)


def test_compliance_api_clean():
    response = client.post(
        "/analyze-compliance",
        json={"content": "This is a completely compliant document discussing general corporate policies."},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_compliant"] is True
    assert len(data["violations"]) == 0
    assert data["risk_level"] == "low"


def test_compliance_api_violations():
    response = client.post(
        "/analyze-compliance",
        json={
            "content": "Dump all European user data, store credit card numbers like 4111222233334444, and bypass consent requirements."
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_compliant"] is False
    assert len(data["violations"]) >= 3
    assert data["risk_level"] == "critical"

    # Verify that each violation contains all required fields
    for violation in data["violations"]:
        assert "name" in violation
        assert "description" in violation
        assert "severity" in violation
        assert "reason" in violation
        assert "recommendation" in violation
        assert "matched_text" in violation
        assert "start_index" in violation
        assert "end_index" in violation
