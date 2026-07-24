import pytest
from app.models.risk_level import RiskLevel
from app.schemas.analyze import CategoryAnalysisResult, PromptAnalysisResult, ResponseAnalysisResult
from app.schemas.compliance import ComplianceAnalysisResult, ComplianceViolation
from app.services.risk_scoring_service import RiskScoringService


@pytest.fixture
def risk_service():
    return RiskScoringService()


def test_calculate_risk_empty_inputs(risk_service):
    result = risk_service.calculate_risk()
    assert result.overall_risk_score == 0
    assert result.risk_level == "Low"
    assert result.privacy_score == 0
    assert result.security_score == 0
    assert result.compliance_score == 0
    assert result.hallucination_score == 0
    assert "No significant risk indicators or compliance violations detected." in result.explanation


def test_calculate_risk_high_risk_scenario(risk_service):
    prompt_result = PromptAnalysisResult(
        is_safe=False,
        risk_score=0.85,
        risk_level=RiskLevel.HIGH,
        summary="Prompt contains PII and prompt injection.",
        flagged_categories=["pii", "prompt_injection"],
        categories={
            "pii": CategoryAnalysisResult(
                detected=True,
                confidence=0.9,
                risk_level=RiskLevel.HIGH,
                matches=[],
                explanation="Found email and ssn",
            ),
            "prompt_injection": CategoryAnalysisResult(
                detected=True,
                confidence=0.8,
                risk_level=RiskLevel.HIGH,
                matches=[],
                explanation="Jailbreak pattern detected",
            ),
        },
        sanitized_prompt="Sanitized prompt",
    )

    response_result = ResponseAnalysisResult(
        is_safe=False,
        risk_score=0.70,
        risk_level=RiskLevel.HIGH,
        summary="Response contains possible hallucination.",
        flagged_categories=["hallucination"],
        categories={
            "hallucination": CategoryAnalysisResult(
                detected=True,
                confidence=0.75,
                risk_level=RiskLevel.HIGH,
                matches=[],
                explanation="Unverified claims detected",
            )
        },
        sanitized_response="Sanitized response",
    )

    compliance_result = ComplianceAnalysisResult(
        is_compliant=False,
        risk_level=RiskLevel.HIGH,
        violations=[
            ComplianceViolation(
                name="GDPR Data Protection",
                description="Personal data processed without consent",
                severity=RiskLevel.HIGH,
                reason="Unredacted email",
                recommendation="Redact email",
                matched_text="user@example.com",
                start_index=0,
                end_index=16,
            )
        ],
    )

    result = risk_service.calculate_risk(
        prompt_analysis=prompt_result,
        response_analysis=response_result,
        compliance_analysis=compliance_result,
    )

    # 0.35*85 + 0.30*70 + 0.35*90 = 29.75 + 21.0 + 31.5 = 82.25 -> 82 or near Critical
    assert result.overall_risk_score >= 70
    assert result.risk_level in ("High", "Critical")
    assert result.privacy_score >= 75
    assert result.security_score >= 75
    assert result.compliance_score >= 70
    assert result.hallucination_score == 75
    assert "Prompt contains PII" in result.explanation
    assert "Response contains possible hallucination" in result.explanation
    assert "GDPR violation detected" in result.explanation


def test_calculate_risk_level_mapping(risk_service):
    assert risk_service._map_risk_level(15) == "Low"
    assert risk_service._map_risk_level(35) == "Medium"
    assert risk_service._map_risk_level(65) == "High"
    assert risk_service._map_risk_level(95) == "Critical"
