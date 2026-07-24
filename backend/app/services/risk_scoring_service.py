import math
from typing import List

from app.models.risk_level import RiskLevel
from app.schemas.analyze import PromptAnalysisResult, ResponseAnalysisResult
from app.schemas.compliance import ComplianceAnalysisResult
from app.schemas.risk_scoring import RiskScoringResult


class RiskScoringService:
    """Service responsible for calculating unified risk scores, sub-scores,

    categorical risk levels, and human-readable explanations.
    """

    WEIGHT_PROMPT = 0.35
    WEIGHT_RESPONSE = 0.30
    WEIGHT_COMPLIANCE = 0.35

    def calculate_risk(
        self,
        prompt_analysis: PromptAnalysisResult | None = None,
        response_analysis: ResponseAnalysisResult | None = None,
        compliance_analysis: ComplianceAnalysisResult | None = None,
    ) -> RiskScoringResult:
        """Calculates component risk scores, weighted overall risk score, risk level,

        and human-readable explanations.
        """
        explanations: List[str] = []

        # 1. Prompt Risk Score
        prompt_score = self._compute_prompt_risk(prompt_analysis, explanations)

        # 2. Response Risk Score
        response_score = self._compute_response_risk(response_analysis, explanations)

        # 3. Compliance Risk Score
        compliance_score = self._compute_compliance_risk(compliance_analysis, explanations)

        # 4. Privacy Risk Score
        privacy_score = self._compute_privacy_risk(prompt_analysis, response_analysis, compliance_analysis)

        # 5. Security Risk Score
        security_score = self._compute_security_risk(prompt_analysis, response_analysis, compliance_analysis)

        # 6. Hallucination Risk Score
        hallucination_score = self._compute_hallucination_risk(response_analysis)

        # 7. Overall Risk Score (Weighted)
        overall_risk_score = self._compute_overall_score(
            prompt_score, response_score, compliance_score, prompt_analysis, response_analysis, compliance_analysis
        )

        # 8. Categorical Risk Level
        risk_level = self._map_risk_level(overall_risk_score)

        # Deduplicate explanations preserving order
        unique_explanations: List[str] = []
        for exp in explanations:
            if exp not in unique_explanations:
                unique_explanations.append(exp)

        if not unique_explanations:
            unique_explanations.append("No significant risk indicators or compliance violations detected.")

        return RiskScoringResult(
            overall_risk_score=overall_risk_score,
            risk_level=risk_level,
            privacy_score=privacy_score,
            security_score=security_score,
            compliance_score=compliance_score,
            hallucination_score=hallucination_score,
            explanation=unique_explanations,
        )

    def _compute_prompt_risk(
        self, prompt_analysis: PromptAnalysisResult | None, explanations: List[str]
    ) -> int:
        if prompt_analysis is None:
            return 0

        base_score = int(round(prompt_analysis.risk_score * 100))

        flagged = set(prompt_analysis.flagged_categories)
        if "pii" in flagged or self._is_category_detected(prompt_analysis.categories, "pii"):
            explanations.append("Prompt contains PII")
        if "prompt_injection" in flagged or "jailbreak" in flagged or self._is_category_detected(prompt_analysis.categories, "prompt_injection"):
            explanations.append("Prompt contains prompt injection or jailbreak attempt")
        if "secrets" in flagged or self._is_category_detected(prompt_analysis.categories, "secrets"):
            explanations.append("Prompt contains sensitive company secrets or credentials")
        if "toxicity" in flagged or self._is_category_detected(prompt_analysis.categories, "toxicity"):
            explanations.append("Prompt contains toxic or unsafe language")

        for cat_name in flagged:
            if cat_name not in {"pii", "prompt_injection", "jailbreak", "secrets", "toxicity"}:
                explanations.append(f"Prompt flagged for {cat_name.replace('_', ' ')}")

        return max(0, min(100, base_score))

    def _compute_response_risk(
        self, response_analysis: ResponseAnalysisResult | None, explanations: List[str]
    ) -> int:
        if response_analysis is None:
            return 0

        base_score = int(round(response_analysis.risk_score * 100))

        flagged = set(response_analysis.flagged_categories)
        if "hallucination" in flagged or self._is_category_detected(response_analysis.categories, "hallucination"):
            explanations.append("Response contains possible hallucination")
        if "pii" in flagged or self._is_category_detected(response_analysis.categories, "pii"):
            explanations.append("Response contains PII leakage")
        if "secrets" in flagged or self._is_category_detected(response_analysis.categories, "secrets"):
            explanations.append("Response contains leaked secrets or credentials")
        if "unsafe_content" in flagged or "toxicity" in flagged or self._is_category_detected(response_analysis.categories, "unsafe_content"):
            explanations.append("Response contains unsafe or toxic content")

        for cat_name in flagged:
            if cat_name not in {"hallucination", "pii", "secrets", "unsafe_content", "toxicity"}:
                explanations.append(f"Response flagged for {cat_name.replace('_', ' ')}")

        return max(0, min(100, base_score))

    def _compute_compliance_risk(
        self, compliance_analysis: ComplianceAnalysisResult | None, explanations: List[str]
    ) -> int:
        if compliance_analysis is None:
            return 0

        if compliance_analysis.is_compliant and not compliance_analysis.violations:
            return 0

        # Calculate violation severity points
        severity_weights = {
            RiskLevel.CRITICAL: 40,
            RiskLevel.HIGH: 25,
            RiskLevel.MODERATE: 15,
            RiskLevel.LOW: 5,
        }

        baseline_map = {
            RiskLevel.CRITICAL: 85,
            RiskLevel.HIGH: 65,
            RiskLevel.MODERATE: 35,
            RiskLevel.LOW: 15,
        }

        base_score = baseline_map.get(compliance_analysis.risk_level, 20)
        violation_points = sum(severity_weights.get(v.severity, 10) for v in compliance_analysis.violations)
        total_score = base_score + violation_points

        for v in compliance_analysis.violations:
            name_lower = v.name.lower()
            desc_lower = v.description.lower()
            if "gdpr" in name_lower or "gdpr" in desc_lower:
                explanations.append("GDPR violation detected")
            elif "hipaa" in name_lower or "hipaa" in desc_lower:
                explanations.append("HIPAA violation detected")
            elif "pci" in name_lower or "pci" in desc_lower:
                explanations.append("PCI-DSS violation detected")
            else:
                explanations.append(f"{v.name} violation detected")

        return max(0, min(100, total_score))

    def _compute_privacy_risk(
        self,
        prompt_analysis: PromptAnalysisResult | None,
        response_analysis: ResponseAnalysisResult | None,
        compliance_analysis: ComplianceAnalysisResult | None,
    ) -> int:
        score = 0

        if prompt_analysis and ("pii" in prompt_analysis.flagged_categories or self._is_category_detected(prompt_analysis.categories, "pii")):
            cat_score = self._get_category_risk_score(prompt_analysis.categories, "pii")
            score = max(score, cat_score or 80)

        if response_analysis and ("pii" in response_analysis.flagged_categories or self._is_category_detected(response_analysis.categories, "pii")):
            cat_score = self._get_category_risk_score(response_analysis.categories, "pii")
            score = max(score, cat_score or 85)

        if compliance_analysis and compliance_analysis.violations:
            for v in compliance_analysis.violations:
                text = (v.name + " " + v.description).lower()
                if "gdpr" in text or "hipaa" in text or "pii" in text or "privacy" in text:
                    score = max(score, 75)

        return max(0, min(100, score))

    def _compute_security_risk(
        self,
        prompt_analysis: PromptAnalysisResult | None,
        response_analysis: ResponseAnalysisResult | None,
        compliance_analysis: ComplianceAnalysisResult | None,
    ) -> int:
        score = 0

        if prompt_analysis:
            for sec_cat in ("prompt_injection", "secrets", "jailbreak"):
                if sec_cat in prompt_analysis.flagged_categories or self._is_category_detected(prompt_analysis.categories, sec_cat):
                    cat_score = self._get_category_risk_score(prompt_analysis.categories, sec_cat)
                    score = max(score, cat_score or 80)

        if response_analysis:
            for sec_cat in ("secrets", "unsafe_content"):
                if sec_cat in response_analysis.flagged_categories or self._is_category_detected(response_analysis.categories, sec_cat):
                    cat_score = self._get_category_risk_score(response_analysis.categories, sec_cat)
                    score = max(score, cat_score or 80)

        if compliance_analysis and compliance_analysis.violations:
            for v in compliance_analysis.violations:
                text = (v.name + " " + v.description).lower()
                if "pci" in text or "security" in text or "secret" in text:
                    score = max(score, 70)

        return max(0, min(100, score))

    def _compute_hallucination_risk(
        self, response_analysis: ResponseAnalysisResult | None
    ) -> int:
        if response_analysis is None:
            return 0

        if "hallucination" in response_analysis.flagged_categories or self._is_category_detected(response_analysis.categories, "hallucination"):
            cat_score = self._get_category_risk_score(response_analysis.categories, "hallucination")
            return cat_score or int(round(response_analysis.risk_score * 100))

        return 0

    def _compute_overall_score(
        self,
        prompt_score: int,
        response_score: int,
        compliance_score: int,
        prompt_analysis: PromptAnalysisResult | None,
        response_analysis: ResponseAnalysisResult | None,
        compliance_analysis: ComplianceAnalysisResult | None,
    ) -> int:
        active_weights = 0.0
        weighted_sum = 0.0

        if prompt_analysis is not None:
            active_weights += self.WEIGHT_PROMPT
            weighted_sum += self.WEIGHT_PROMPT * prompt_score

        if response_analysis is not None:
            active_weights += self.WEIGHT_RESPONSE
            weighted_sum += self.WEIGHT_RESPONSE * response_score

        if compliance_analysis is not None:
            active_weights += self.WEIGHT_COMPLIANCE
            weighted_sum += self.WEIGHT_COMPLIANCE * compliance_score

        if active_weights == 0.0:
            return 0

        final_score = int(round(weighted_sum / active_weights))
        return max(0, min(100, final_score))

    def _map_risk_level(self, score: int) -> str:
        if score <= 20:
            return "Low"
        if score <= 50:
            return "Medium"
        if score <= 80:
            return "High"
        return "Critical"

    @staticmethod
    def _is_category_detected(categories: dict, category_name: str) -> bool:
        if category_name in categories:
            cat = categories[category_name]
            return getattr(cat, "detected", False)
        return False

    @staticmethod
    def _get_category_risk_score(categories: dict, category_name: str) -> int | None:
        if category_name in categories:
            cat = categories[category_name]
            if getattr(cat, "detected", False):
                conf = getattr(cat, "confidence", 0.8)
                return int(round(conf * 100))
        return None
