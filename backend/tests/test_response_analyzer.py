import pytest
from app.models.risk_level import RiskLevel
from app.services.response_analyzer import ResponseAnalyzer


@pytest.fixture
def analyzer() -> ResponseAnalyzer:
    return ResponseAnalyzer()


def test_clean_safe_response(analyzer: ResponseAnalyzer):
    prompt = "Explain how gravity works."
    response = "Gravity is a fundamental force of nature that attracts objects with mass toward each other."
    result = analyzer.analyze_response(response, prompt=prompt)

    assert result.is_safe is True
    assert result.risk_level == RiskLevel.LOW
    assert result.risk_score == 0.0
    assert len(result.flagged_categories) == 0
    assert result.sanitized_response == response


def test_hallucination_detection(analyzer: ResponseAnalyzer):
    prompt = "Tell me about the event in 1990."
    response = "It is a 100% indisputable fact that this event occurred in 2024 as proven by doi:10.9999/fake-paper."
    result = analyzer.analyze_response(response, prompt=prompt)

    assert result.is_safe is False
    assert "hallucination_risk" in result.flagged_categories
    hal_res = result.categories["hallucination_risk"]
    assert hal_res.detected is True


def test_bias_detection(analyzer: ResponseAnalyzer):
    response = "When hiring engineering leaders, you should prefer male candidates because women are naturally unsuited for leadership."
    result = analyzer.analyze_response(response)

    assert result.is_safe is False
    assert "bias" in result.flagged_categories
    bias_res = result.categories["bias"]
    assert bias_res.detected is True
    assert bias_res.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL)


def test_toxicity_detection(analyzer: ResponseAnalyzer):
    response = "Shut up! You are a fucking idiot for asking such a stupid question."
    result = analyzer.analyze_response(response)

    assert result.is_safe is False
    assert "toxicity" in result.flagged_categories
    tox_res = result.categories["toxicity"]
    assert tox_res.detected is True


def test_sensitive_information_detection(analyzer: ResponseAnalyzer):
    response = "Here is the user email john.smith@company.com and OpenAI API key sk-proj-1234567890abcdef1234567890abcdef."
    result = analyzer.analyze_response(response)

    assert result.is_safe is False
    assert "sensitive_information" in result.flagged_categories
    sens_res = result.categories["sensitive_information"]
    assert sens_res.detected is True
    assert "[REDACTED_EMAIL]" in result.sanitized_response
    assert "[REDACTED_OPENAI_KEY]" in result.sanitized_response


def test_unsafe_content_detection(analyzer: ResponseAnalyzer):
    response = "Here is the script for a keylogger Python program that logs keystrokes..."
    result = analyzer.analyze_response(response)

    assert result.is_safe is False
    assert "unsafe_content" in result.flagged_categories
    unsafe_res = result.categories["unsafe_content"]
    assert unsafe_res.detected is True


def test_compliance_violations_detection(analyzer: ResponseAnalyzer):
    response = "You have cancer. Take amoxicillin 500mg three times daily."
    result = analyzer.analyze_response(response)

    assert result.is_safe is False
    assert "compliance_violations" in result.flagged_categories
    comp_res = result.categories["compliance_violations"]
    assert comp_res.detected is True
