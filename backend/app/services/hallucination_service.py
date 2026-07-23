import re
from typing import List, Tuple

from app.schemas.hallucination import DetectHallucinationRequest, DetectHallucinationResponse, FlaggedClaim


class HallucinationService:
    """Service for performing rule-based hallucination detection on AI-generated text."""

    FACTUAL_CONTRADICTIONS = [
        (
            r"(?i)eiffel tower.*(in|located in|built in)\s+(berlin|london|rome|madrid|tokyo|new york)",
            "The Eiffel Tower is located in Paris, France, not Berlin.",
        ),
        (
            r"(?i)statue of liberty.*(in|located in)\s+(london|paris|berlin|tokyo)",
            "The Statue of Liberty is located in New York, USA.",
        ),
        (
            r"(?i)taj mahal.*(in|located in)\s+(new york|london|paris|tokyo|berlin)",
            "The Taj Mahal is located in Agra, India.",
        ),
        (
            r"(?i)great wall of china.*(in|located in)\s+(brazil|japan|india|australia|mexico)",
            "The Great Wall of China is located in China.",
        ),
        (
            r"(?i)pyramids of giza.*(in|located in)\s+(australia|japan|brazil|canada|germany)",
            "The Pyramids of Giza are located in Egypt.",
        ),
        (r"(?i)earth is (flat|cube|square)", "Scientific consensus confirms Earth is an oblate spheroid."),
        (r"(?i)sun (revolves|orbits) (around|about) (the )?earth", "Earth revolves around the Sun."),
        (r"(?i)2\s*\+\s*2\s*=\s*5", "Mathematical contradiction: 2 + 2 = 4."),
        (r"(?i)moon is (made of|composed of)\s+cheese", "The Moon is composed of rock and metal."),
    ]

    ABSOLUTE_PATTERNS = [
        (
            r"(?i)\b(always|never|guaranteed|100%\s+true|definitely\s+without\s+doubt|completely\s+impossible)\b",
            "Absolute claim made without necessary nuance or caveats.",
        ),
        (
            r"(?i)\b(undeniable\s+fact|beyond\s+any\s+question|absolutely\s+certain|indisputable\s+truth)\b",
            "Overconfident language indicating potential hallucinated certainty.",
        ),
    ]

    NUMERICAL_PATTERNS = [
        (
            r"(?i)\b(studies\s+prove\s+99\.9%|100%\s+of\s+scientists\s+agree|exact\s+probability\s+is\s+99\.999%)\b",
            "Unsupported precise statistical or numerical assertion.",
        ),
        (r"(?i)\b(\d{10,})\b", "Suspiciously long or precise unverified numeric sequence."),
    ]

    UNCITED_PATTERNS = [
        (
            r"(?i)\b(research\s+shows|studies\s+prove|according\s+to\s+experts|scientists\s+discovered)\b",
            "Vague citation of research or studies without providing a specific reference or source.",
        ),
    ]

    CITATION_PATTERNS = [
        (
            r"\[\d+\]|\[citation\s+needed\]|\[ref\]|\[source\]",
            "Unresolved or empty citation marker found without supporting reference source.",
        ),
        (
            r"(?i)\b(journal\s+of\s+\w+\s+science|et\s+al\.\s*\((20[4-9]\d|21\d\d)\))\b",
            "Fabricated or impossible future publication date/citation.",
        ),
    ]

    def detect_hallucination(self, request: DetectHallucinationRequest) -> DetectHallucinationResponse:
        text = request.response.strip()
        flagged_claims: List[FlaggedClaim] = []

        self._check_factual_contradictions(text, flagged_claims)
        self._check_absolute_statements(text, flagged_claims)
        self._check_numerical_claims(text, flagged_claims)
        self._check_uncited_claims(text, flagged_claims)
        self._check_citations(text, flagged_claims)

        hallucination_detected = len(flagged_claims) > 0

        if not hallucination_detected:
            return DetectHallucinationResponse(
                hallucination_detected=False,
                confidence=0.0,
                risk_level="Low",
                summary="No significant indicators of hallucination or unsupported claims detected.",
                flagged_claims=[],
                recommendation="Response appears coherent and free of obvious heuristic risk indicators.",
            )

        confidence, risk_level = self._compute_confidence_and_risk(flagged_claims)
        summary = self._generate_summary(flagged_claims)
        recommendation = "Verify factual statements using trusted external sources before presenting them to users."

        return DetectHallucinationResponse(
            hallucination_detected=True,
            confidence=confidence,
            risk_level=risk_level,
            summary=summary,
            flagged_claims=flagged_claims,
            recommendation=recommendation,
        )

    def _check_factual_contradictions(self, text: str, flagged_claims: List[FlaggedClaim]) -> None:
        for pattern, reason in self.FACTUAL_CONTRADICTIONS:
            match = re.search(pattern, text)
            if match:
                snippet = self._get_sentence_snippet(text, match.start(), match.end())
                flagged_claims.append(
                    FlaggedClaim(
                        claim=snippet,
                        reason=f"Known factual inconsistency. {reason}",
                    )
                )

    def _check_absolute_statements(self, text: str, flagged_claims: List[FlaggedClaim]) -> None:
        for pattern, reason in self.ABSOLUTE_PATTERNS:
            for match in re.finditer(pattern, text):
                snippet = self._get_sentence_snippet(text, match.start(), match.end())
                flagged_claims.append(
                    FlaggedClaim(
                        claim=snippet,
                        reason=reason,
                    )
                )

    def _check_numerical_claims(self, text: str, flagged_claims: List[FlaggedClaim]) -> None:
        for pattern, reason in self.NUMERICAL_PATTERNS:
            for match in re.finditer(pattern, text):
                snippet = self._get_sentence_snippet(text, match.start(), match.end())
                flagged_claims.append(
                    FlaggedClaim(
                        claim=snippet,
                        reason=reason,
                    )
                )

    def _check_uncited_claims(self, text: str, flagged_claims: List[FlaggedClaim]) -> None:
        has_sources = bool(re.search(r"(?i)(https?://|doi:|references:|sources:)", text))
        if not has_sources:
            for pattern, reason in self.UNCITED_PATTERNS:
                for match in re.finditer(pattern, text):
                    snippet = self._get_sentence_snippet(text, match.start(), match.end())
                    flagged_claims.append(
                        FlaggedClaim(
                            claim=snippet,
                            reason=reason,
                        )
                    )

    def _check_citations(self, text: str, flagged_claims: List[FlaggedClaim]) -> None:
        for pattern, reason in self.CITATION_PATTERNS:
            for match in re.finditer(pattern, text):
                snippet = self._get_sentence_snippet(text, match.start(), match.end())
                flagged_claims.append(
                    FlaggedClaim(
                        claim=snippet,
                        reason=reason,
                    )
                )

    def _get_sentence_snippet(self, text: str, start: int, end: int) -> str:
        sentence_start = max(0, text.rfind(".", 0, start) + 1)
        sentence_end = text.find(".", end)
        if sentence_end == -1:
            sentence_end = len(text)
        else:
            sentence_end += 1

        snippet = text[sentence_start:sentence_end].strip()
        return snippet if snippet else text[start:end].strip()

    def _compute_confidence_and_risk(self, flagged_claims: List[FlaggedClaim]) -> Tuple[float, str]:
        count = len(flagged_claims)
        has_factual_error = any("factual inconsistency" in claim.reason.lower() for claim in flagged_claims)

        if has_factual_error:
            confidence = min(0.95, 0.88 + (count * 0.02))
            risk_level = "High" if confidence < 0.93 else "Critical"
        elif count >= 3:
            confidence = min(0.90, 0.70 + (count * 0.05))
            risk_level = "High"
        elif count == 2:
            confidence = 0.75
            risk_level = "Medium"
        else:
            confidence = 0.60
            risk_level = "Medium"

        return round(confidence, 2), risk_level

    def _generate_summary(self, flagged_claims: List[FlaggedClaim]) -> str:
        has_factual = any("factual inconsistency" in c.reason.lower() for c in flagged_claims)
        if has_factual:
            return "The response contains statements that appear factually inconsistent or unsupported."
        return "The response contains overconfident, absolute, or uncited statements that may indicate hallucination."
