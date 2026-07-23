import re
from typing import List, Tuple

from app.schemas.analyze import AnalyzePromptRequest, PromptAnalysisResult
from app.schemas.prompt_improvement import ImprovePromptRequest, ImprovePromptResponse
from app.services.prompt_analysis_service import PromptAnalysisService


class PromptImprovementService:
    """Service for analyzing unsafe prompts and applying deterministic,
    rule-based transformations to produce safe, intent-preserving prompts.
    """

    def __init__(self, analysis_service: PromptAnalysisService | None = None) -> None:
        self.analysis_service = analysis_service or PromptAnalysisService()

    def improve_prompt(self, request: ImprovePromptRequest) -> ImprovePromptResponse:
        prompt = request.prompt.strip()

        # 1. Reuse Prompt Analysis Service
        analysis: PromptAnalysisResult = self.analysis_service.analyze_prompt(
            AnalyzePromptRequest(prompt=prompt)
        )

        # 2. Check if prompt is already safe
        if analysis.is_safe:
            return ImprovePromptResponse(
                original_prompt=prompt,
                risk_summary=[],
                unsafe_reason="Prompt is safe and compliant.",
                improved_prompt=prompt,
                alternative_prompts=[],
                message="Prompt is already safe.",
            )

        # 3. Process Unsafe Prompt
        risk_summary = self._build_risk_summary(analysis)
        unsafe_reason = self._build_unsafe_reason(analysis, risk_summary)

        # 4. Perform Rule-Based Rewriting
        improved_prompt, alternatives = self._generate_safe_rewrites(prompt, analysis, risk_summary)

        return ImprovePromptResponse(
            original_prompt=prompt,
            risk_summary=risk_summary,
            unsafe_reason=unsafe_reason,
            improved_prompt=improved_prompt,
            alternative_prompts=alternatives,
        )

    def _build_risk_summary(self, analysis: PromptAnalysisResult) -> List[str]:
        risk_map = {
            "prompt_injection": "Prompt Injection",
            "jailbreak": "Jailbreak Attempt",
            "secrets": "Sensitive Information Request",
            "pii": "PII Exposure Request",
            "toxicity": "Toxic Language",
            "unsafe_content": "Unsafe Request",
        }
        summary = []
        for cat in analysis.flagged_categories:
            cat_clean = cat.lower()
            if cat_clean in risk_map:
                summary.append(risk_map[cat_clean])
            else:
                summary.append(cat.replace("_", " ").title())

        if not summary:
            for cat_name, details in analysis.categories.items():
                if getattr(details, "detected", False):
                    cat_clean = cat_name.lower()
                    summary.append(risk_map.get(cat_clean, cat_name.replace("_", " ").title()))

        result = []
        for item in summary:
            if item not in result:
                result.append(item)

        return result if result else ["Unsafe Request"]

    def _build_unsafe_reason(self, analysis: PromptAnalysisResult, risk_summary: List[str]) -> str:
        reasons = []
        if "Prompt Injection" in risk_summary or "Jailbreak Attempt" in risk_summary:
            reasons.append("attempts to bypass system instructions")
        if "Sensitive Information Request" in risk_summary:
            reasons.append("requests confidential information")
        if "PII Exposure Request" in risk_summary:
            reasons.append("requests personally identifiable information")
        if "Toxic Language" in risk_summary or "Unsafe Request" in risk_summary:
            reasons.append("contains toxic or unsafe language")

        if reasons:
            if len(reasons) == 1:
                return f"The prompt {reasons[0]}."
            return f"The prompt {' and '.join(reasons)}."

        return analysis.summary or "The prompt violates security or compliance policies."

    def _generate_safe_rewrites(
        self, prompt: str, analysis: PromptAnalysisResult, risk_summary: List[str]
    ) -> Tuple[str, List[str]]:
        cleaned = self._strip_injection_patterns(prompt)
        topic = self._extract_core_topic(cleaned, prompt)

        if "Sensitive Information Request" in risk_summary or "Prompt Injection" in risk_summary:
            improved = f"Explain cybersecurity best practices for protecting {topic} without requesting confidential information."
            alternatives = [
                f"What are standard administrative procedures for managing internal {topic} securely?",
                f"Provide an overview of {topic} security mechanisms and credential protection protocols.",
                f"Discuss educational concepts behind {topic} security in enterprise systems.",
            ]
        elif "PII Exposure Request" in risk_summary:
            improved = f"Explain data privacy guidelines and compliance policies regarding {topic}."
            alternatives = [
                f"What are best practices for anonymizing sensitive personal data such as {topic}?",
                f"Provide general information on data privacy regulations for {topic}.",
                f"How should organizations protect user privacy when processing {topic}?",
            ]
        elif "Toxic Language" in risk_summary:
            improved = f"Provide a constructive, professional overview of {topic}."
            alternatives = [
                f"What are key neutral perspective details regarding {topic}?",
                f"Explain {topic} in an objective and respectful manner.",
                f"Discuss the fundamental principles of {topic} without offensive terminology.",
            ]
        else:
            improved = f"Explain the technical concepts and safety considerations related to {topic}."
            alternatives = [
                f"What are standard defensive and educational concepts regarding {topic}?",
                f"Discuss standard safety frameworks concerning {topic}.",
                f"Provide a high-level overview of security controls for {topic}.",
            ]

        return improved, alternatives

    def _strip_injection_patterns(self, prompt: str) -> str:
        patterns = [
            r"(?i)ignore\s+(all\s+)?(previous|prior|above)\s+instructions\s+(and\s+)?",
            r"(?i)disregard\s+(all\s+)?system\s+prompts?\s+(and\s+)?",
            r"(?i)you\s+are\s+now\s+(in\s+)?dan\s+mode\s+(and\s+)?",
            r"(?i)override\s+safety\s+filters?\s+(and\s+)?",
            r"(?i)act\s+as\s+an?\s+unrestricted\s+ai\s+(and\s+)?",
            r"(?i)do\s+anything\s+now\s+(and\s+)?",
            r"(?i)developer\s+mode\s+(enabled|on)\s+(and\s+)?",
            r"(?i)bypass\s+(rules|restrictions|governance)\s+(and\s+)?",
        ]
        cleaned = prompt
        for pat in patterns:
            cleaned = re.sub(pat, "", cleaned)
        return cleaned.strip()

    def _extract_core_topic(self, cleaned_prompt: str, original_prompt: str) -> str:
        text = cleaned_prompt if cleaned_prompt else original_prompt
        low = text.lower()

        if "password" in low or "credential" in low:
            return "passwords"
        if "secret" in low or "key" in low or "token" in low:
            return "system secrets and API keys"
        if "pii" in low or "ssn" in low or "email" in low or "phone" in low:
            return "personal data"
        if "database" in low or "sql" in low:
            return "database security"
        if "network" in low or "firewall" in low:
            return "network configuration"
        if "system" in low or "architecture" in low:
            return "system architecture"

        match = re.search(
            r"(?:reveal|show|give|display|get|provide)\s+(?:the\s+|all\s+|internal\s+|system\s+)?([a-zA-Z0-9_\s]{3,30})",
            text,
            re.IGNORECASE,
        )
        if match:
            topic = match.group(1).strip()
            if topic:
                return topic

        words = [
            w
            for w in text.split()
            if len(w) > 3 and w.lower() not in {"ignore", "previous", "instructions", "reveal", "show", "give", "please"}
        ]
        if words:
            return " ".join(words[-3:]).lower()

        return "system security"
