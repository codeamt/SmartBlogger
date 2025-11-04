import hashlib
import json
import logging
import re
from typing import Dict, List, Set, Optional
from .llm_manager import local_llm_manager
from config import PLAGIARISM_THRESHOLD

# Logger for the module
log = logging.getLogger(__name__)


class PlagiarismDetector:
    def __init__(self, llm_manager=None, threshold: Optional[int] = None):
        self.llm_manager = llm_manager or local_llm_manager
        self.llm = self.llm_manager.get_researcher()
        self.threshold = threshold if threshold is not None else PLAGIARISM_THRESHOLD

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
        """AI-powered plagiarism analysis with enhanced detection"""
        prompt = f"""
        Analyze this content for plagiarism risk with detailed evaluation.

        CONTENT:
        {content[:3000]}

        Provide analysis in JSON format strictly as:
        {{
            "risk_score": 0-100,
            "flagged_phrases": ["list of potentially unoriginal phrases"],
            "confidence": "high"|"medium"|"low",
            "issues": ["list of specific plagiarism issues found"],
            "suggestions": ["specific suggestions for improvement"]
        }}
        
        Evaluation criteria:
        1. Originality of phrasing and sentence structures
        2. Presence and quality of citations and references
        3. Sentence variety and complexity
        4. Repetitive patterns or formulaic language
        5. Unusual similarity to common educational or web content
        6. Proper attribution of ideas and quotes
        
        Risk Score Guidelines:
        0-20: Low risk - mostly original content
        21-50: Medium risk - some unoriginal elements
        51-80: High risk - significant plagiarism concerns
        81-100: Very high risk - extensive plagiarism detected
        """
        try:
            response = self.llm.invoke([
                ("system", "You are a plagiarism detection expert. Output valid JSON only. Be thorough and precise in your analysis."),
                ("human", prompt),
            ])
            data = json.loads(response.content)
            # Basic shape guard
            if not isinstance(data, dict):
                return {"risk_score": 0, "flagged_phrases": [], "confidence": "low", "issues": [], "suggestions": []}
            data.setdefault("risk_score", 0)
            data.setdefault("flagged_phrases", [])
            data.setdefault("confidence", "low")
            data.setdefault("issues", [])
            data.setdefault("suggestions", [])
            return data
        except Exception as e:
            print(f"AI plagiarism check failed: {e}")
            return {"risk_score": 0, "flagged_phrases": [], "confidence": "low", "issues": [], "suggestions": []}

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
        """Analyze content structure for plagiarism indicators and return detailed recommendations"""
        recs: List[str] = []
        words = content.split()
        word_count = len(words)
        
        # Check for repetition
        if word_count > 800 and len(set(words)) / max(word_count, 1) < 0.4:
            recs.append("High repetition detected; paraphrase and vary sentence structures.")
        
        # Check for citations
        if "http" not in content and "cite" not in content.lower() and word_count > 300:
            recs.append("Consider adding citations or references for key claims.")
        
        # Check for code blocks
        if any(block in content for block in ["```", "\nclass ", "\ndef "]):
            recs.append("Large code blocks detected; add explanatory narration and cite sources if adapted.")
        
        # Check for formulaic phrasing
        formulaic_phrases = ["in conclusion", "as previously stated", "in summary", "as mentioned earlier", 
                           "it is important to note", "it should be noted that", "in order to", "due to the fact that"]
        formulaic_count = sum(1 for phrase in formulaic_phrases if phrase in content.lower())
        if formulaic_count > 3:
            recs.append(f"{formulaic_count} formulaic phrases detected; rewrite with more original language.")
        
        # Check for sentence length variety
        sentences = re.split(r'[.!?]+', content)
        sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
        if sentence_lengths and len(set(sentence_lengths)) / len(sentence_lengths) < 0.5:
            recs.append("Low sentence length variety detected; mix short and long sentences for better flow.")
        
        # Check for paragraph length consistency
        paragraphs = content.split('\n\n')
        paragraph_lengths = [len(p.split()) for p in paragraphs if p.strip()]
        if len(paragraph_lengths) > 3:
            avg_length = sum(paragraph_lengths) / len(paragraph_lengths)
            if any(abs(length - avg_length) / avg_length > 0.8 for length in paragraph_lengths):
                recs.append("Inconsistent paragraph lengths detected; aim for more balanced structure.")
        
        return recs


# Global instance
plagiarism_detector = PlagiarismDetector()
