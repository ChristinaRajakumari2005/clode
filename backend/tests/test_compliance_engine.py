import pytest
from app.models.risk_level import RiskLevel
from app.services.compliance_engine import ComplianceEngine


@pytest.fixture
def engine() -> ComplianceEngine:
    return ComplianceEngine()


def test_clean_content(engine: ComplianceEngine):
    result = engine.evaluate("This is clean and standard business documentation.")
    assert result.is_compliant is True
    assert len(result.violations) == 0
    assert result.risk_level == RiskLevel.LOW


def test_gdpr_violations(engine: ComplianceEngine):
    # Test data export and consent bypass
    result = engine.evaluate(
        "We need to export all EU citizen data immediately. Also, we can just bypass GDPR consent requirements."
    )
    assert result.is_compliant is False
    assert len(result.violations) == 2

    # Check GDPR violations fields
    v_export = next(v for v in result.violations if "Export / Scraping" in v.name)
    assert v_export.severity == RiskLevel.HIGH
    assert v_export.description != ""
    assert v_export.reason != ""
    assert v_export.recommendation != ""

    v_bypass = next(v for v in result.violations if "Consent Bypass" in v.name)
    assert v_bypass.severity == RiskLevel.HIGH
    assert v_bypass.reason != ""


def test_hipaa_violations(engine: ComplianceEngine):
    # Test patient records exposure and lack of BAA
    result = engine.evaluate(
        "patient name: John Doe\nmedical history: diabetes\nWe will share medical data without BAA over email."
    )
    assert result.is_compliant is False
    assert len(result.violations) >= 2

    v_phi = next(v for v in result.violations if "PHI" in v.name)
    assert v_phi.severity == RiskLevel.CRITICAL
    assert v_phi.reason != ""

    v_baa = next(v for v in result.violations if "BAA" in v.name)
    assert v_baa.severity == RiskLevel.HIGH
    assert v_baa.recommendation != ""


def test_pci_dss_violations(engine: ComplianceEngine):
    # Test plaintext PAN and CVV code
    result = engine.evaluate("The credit card number is 4111222233334444 and CVV code is: 123")
    assert result.is_compliant is False
    assert len(result.violations) >= 2

    v_pan = next(v for v in result.violations if "PAN" in v.name)
    assert v_pan.severity == RiskLevel.CRITICAL

    v_cvv = next(v for v in result.violations if "Authentication" in v.name)
    assert v_cvv.severity == RiskLevel.CRITICAL


def test_company_policies(engine: ComplianceEngine):
    # Test credentials exposure and insider trading
    result = engine.evaluate(
        "Here is the AWS Key: AKIA1234567890ABCDEF. We should use this to front-run trades using non-public information."
    )
    assert result.is_compliant is False
    assert len(result.violations) >= 2

    v_keys = next(v for v in result.violations if "Credentials" in v.name)
    assert v_keys.severity == RiskLevel.CRITICAL

    v_insider = next(v for v in result.violations if "Insider" in v.name)
    assert v_insider.severity == RiskLevel.HIGH


def test_missing_disclaimer(engine: ComplianceEngine):
    # Test medical trigger without disclaimer
    result = engine.evaluate("You have diabetes. Take insulin daily.")
    assert result.is_compliant is False
    assert len(result.violations) == 1
    assert "Advice Omission" in result.violations[0].name
    assert result.violations[0].severity == RiskLevel.HIGH

    # Test medical trigger WITH disclaimer (should be compliant regarding disclaimers)
    result_with_disclaimer = engine.evaluate(
        "You have diabetes. Take insulin daily. Note: I am not a doctor; consult a physician for medical advice."
    )
    assert result_with_disclaimer.is_compliant is True
