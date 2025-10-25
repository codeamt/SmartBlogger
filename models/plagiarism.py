import hashlib
import json
from typing import Dict, List, Set
from .llm_manager import local_llm_manager


class PlagiarismDetector:
    def __init__(self):
        self.llm = local_llm_manager.get_researcher()

    def analyze_content(self, content: str, existing_fingerprints: Set[str]) -> Dict:
        """Comprehensive plagiarism analysis"""
        analysis: Dict = {
            "risk_score": 0,
            "flagged_phrases": [],
            "fingerprint_match": False,
            "recommendations": [],
            "confidence": "low",
            "overlaps": [],  # list of overlapping n-grams for transparency
        }

        # Content fingerprinting
        fingerprint = self._create_fingerprint(content)
        analysis["fingerprint_match"] = fingerprint in existing_fingerprints

        # N-gram overlap within content (self-similarity / repetition)
        analysis["overlaps"] = self._ngram_overlaps(content, n=5)

        # AI-based analysis
        ai_analysis = self._ai_plagiarism_check(content)
        analysis.update({k: v for k, v in ai_analysis.items() if k in ["risk_score", "flagged_phrases", "confidence"]})

        # Structural analysis
        structural_issues = self._structural_analysis(content)
        analysis["recommendations"].extend(structural_issues)

        return analysis

    def _create_fingerprint(self, content: str) -> str:
        """Create content fingerprint for duplicate detection"""
        normalized = " ".join(content.lower().split())
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]

    def _ai_plagiarism_check(self, content: str) -> Dict:
        """AI-powered plagiarism analysis"""
        prompt = f"""
        Analyze this content for plagiarism risk.

        CONTENT:
        {content[:2000]}

        Provide analysis in JSON format strictly as:
        {{
            "risk_score": 0-100,
            "flagged_phrases": ["list of potentially unoriginal phrases"],
            "confidence": "high"|"medium"|"low"
        }}
        Consider originality of phrasing, presence of citations, and sentence variety.
        """
        try:
            response = self.llm.invoke([
                ("system", "You are a plagiarism detection expert. Output valid JSON only."),
                ("human", prompt),
            ])
            data = json.loads(response.content)
            # Basic shape guard
            if not isinstance(data, dict):
                return {"risk_score": 0, "flagged_phrases": [], "confidence": "low"}
            data.setdefault("risk_score", 0)
            data.setdefault("flagged_phrases", [])
            data.setdefault("confidence", "low")
            return data
        except Exception:
            return {"risk_score": 0, "flagged_phrases": [], "confidence": "low"}

    def _ngram_overlaps(self, content: str, n: int = 5) -> List[str]:
        """Return top repeated n-grams (self-overlap indicator)."""
        words = [w for w in content.lower().split() if w]
        if len(words) < n:
            return []
        counts: Dict[str, int] = {}
        for i in range(len(words) - n + 1):
            gram = " ".join(words[i:i+n])
            counts[gram] = counts.get(gram, 0) + 1
        # Keep n-grams that appear more than once
        repeated = [(g, c) for g, c in counts.items() if c > 1]
        repeated.sort(key=lambda x: x[1], reverse=True)
        return [f"{g} (x{c})" for g, c in repeated[:5]]

    def _structural_analysis(self, content: str) -> List[str]:
        """Analyze content structure for plagiarism indicators and return recommendations"""
        recs: List[str] = []
        words = content.split()
        if len(words) > 800 and len(set(words)) / max(len(words), 1) < 0.4:
            recs.append("High repetition detected; paraphrase and vary sentence structures.")
        if "http" not in content and "cite" not in content.lower():
            recs.append("Consider adding citations or references for key claims.")
        if any(block in content for block in ["```", "\nclass ", "\ndef "]):
            recs.append("Large code blocks detected; add explanatory narration and cite sources if adapted.")
        if any(phrase in content.lower() for phrase in ["in conclusion", "as previously stated"]):
            recs.append("Formulaic phrasing found; rewrite with more original language.")
        return recs


# Global instance
plagiarism_detector = PlagiarismDetector()
