import hashlib
import json
from typing import Dict, List
from ..llm_manager import local_llm_manager


class PlagiarismDetector:
    def __init__(self):
        self.llm = local_llm_manager.get_researcher()

    def analyze_content(self, content: str, existing_fingerprints: set) -> Dict:
        """Comprehensive plagiarism analysis"""
        analysis = {
            "risk_score": 0,
            "flagged_phrases": [],
            "fingerprint_match": False,
            "recommendations": []
        }

        # Content fingerprinting
        fingerprint = self._create_fingerprint(content)
        analysis["fingerprint_match"] = fingerprint in existing_fingerprints

        # AI-based analysis
        ai_analysis = self._ai_plagiarism_check(content)
        analysis.update(ai_analysis)

        # Structural analysis
        structural_issues = self._structural_analysis(content)
        analysis["recommendations"].extend(structural_issues)

        return analysis

    def _create_fingerprint(self, content: str) -> str:
        """Create content fingerprint for duplicate detection"""
        # Normalize content
        normalized = ' '.join(content.lower().split())
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]

    def _ai_plagiarism_check(self, content: str) -> Dict:
        """AI-powered plagiarism analysis"""
        prompt = f"""
        Analyze this content for plagiarism risk:

        CONTENT:
        {content[:2000]}

        Provide analysis in JSON format:
        {{
            "risk_score": 0-100,
            "flagged_phrases": ["list of potentially unoriginal phrases"],
            "confidence": "high/medium/low"
        }}

        Consider:
        - Originality of phrasing
        - Common technical patterns vs copied content
        - Citation adequacy
        - Sentence structure variety
        """

        try:
            response = self.llm.invoke([("system", "You are a plagiarism detection expert. Output valid JSON only."),
                                        ("human", prompt)])
            return json.loads(response.content)
        except:
            return {"risk_score": 0, "flagged_phrases": [], "confidence": "low"}

    def _structural_analysis(self, content: str) -> List[str]:
        """Analyze content structure for plagiarism indicators"""
        feedback = {}
        needs_rewrite = False

        # Check API results
        if "api" in checks and checks["api"].get("score", 0) > state.get("plagiarism_threshold", 15):
            needs_rewrite = True
            feedback += f"API similarity score {checks['api']['score']}% exceeds threshold. "

        # Check AI analysis
        if "ai" in checks and checks["ai"].get("risk_score", 0) > 70:
            needs_rewrite = True
            feedback += f"High AI risk score {checks['ai']['risk_score']}/100. "

        if checks["ai"].get("flagged_phrases"):
            feedback += f"Flagged phrases: {', '.join(checks['ai']['flagged_phrases'][:3])}. "

        if needs_rewrite:
            return {
                **state,
                "plagiarism_feedback": feedback,
                "needs_rewrite": True,
                "next_action": "rewrite_section"
            }
        else:
            # Move to next section or end
            current_index = next(i for i, s in enumerate(state["sections"])
                                 if s["id"] == section_id)
            if current_index + 1 < len(state["sections"]):
                return {
                    **state,
                    "current_section": state["sections"][current_index + 1],
                    "next_action": "draft_section"
                }
            else:
                return {**state, "next_action": "end"}


# Global instance
plagiarism_detector = PlagiarismDetector()