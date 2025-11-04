from state import EnhancedBlogState
from utils.token_tracking import track_token_usage
from models.plagiarism import plagiarism_detector
from models.llm_manager import local_llm_manager
import random
import re
from typing import Dict, Any


def plagiarism_check_node(state: EnhancedBlogState) -> EnhancedBlogState:
    """Smart plagiarism detection with multi-stage cost-effective checking"""
    if not state.current_section:
        return state.update(next_action="completion")

    section_id = state.current_section["id"]
    content = state.section_drafts.get(section_id, "")

    if not content:
        return state.update(next_action="completion")

    # Create content fingerprint
    fingerprint = plagiarism_detector._create_fingerprint(content)
    updated_fingerprints = state.content_fingerprints.copy()
    updated_fingerprints.add(fingerprint)

    # Multi-stage plagiarism analysis
    results = {}
    
    # Stage 1: Local AI analysis (no cost)
    ai_result = plagiarism_detector.analyze_content(content, updated_fingerprints)
    results["ai"] = ai_result
    
    # Stage 2: Quick local similarity checks (no cost)
    local_similarity = _quick_similarity_check(content, state)
    results["local_similarity"] = local_similarity
    
    # Stage 3: Only use API for high-risk content to conserve credits
    if should_check_content(state, content) and _should_use_api_check(ai_result, local_similarity):
        # Simulated API response (replace with actual external checker)
        api_score = _estimate_api_score(content, ai_result, local_similarity)
        results["api"] = {"score": api_score}
        updated_credits = state.free_tier_credits - 1
    else:
        # Use estimated score based on local analysis
        estimated_score = _estimate_plagiarism_score(ai_result, local_similarity)
        results["estimated"] = {"score": estimated_score}
        updated_credits = state.free_tier_credits

    # Update plagiarism checks
    updated_checks = state.plagiarism_checks.copy()
    updated_checks[section_id] = results

    return state.update(
        content_fingerprints=updated_fingerprints,
        plagiarism_checks=updated_checks,
        free_tier_credits=updated_credits,
        next_action="evaluate_plagiarism",
    )


def evaluate_plagiarism_node(state: EnhancedBlogState) -> EnhancedBlogState:
    """Evaluate plagiarism results and decide if rewriting is needed"""
    if not state.current_section:
        return state.update(next_action="completion")

    section_id = state.current_section["id"]
    checks = state.plagiarism_checks.get(section_id, {})

    needs_rewrite = False
    feedback = ""
    
    # Get plagiarism score from any available source
    plagiarism_score = _get_plagiarism_score(checks)
    
    # Check against threshold (use default threshold 15 if not configured)
    if plagiarism_score > 15:
    #if plagiarism_score > int(os.getenv("PLAGIARISM_THRESHOLD", 15)):
        needs_rewrite = True
        feedback += f"Plagiarism risk score {plagiarism_score}% exceeds threshold. "

    # Check AI analysis
    ai = checks.get("ai", {})
    if ai.get("risk_score", 0) > 70:
        needs_rewrite = True
        feedback += f"High AI risk score {ai['risk_score']}/100. "

    flagged = ai.get("flagged_phrases") or []
    if flagged:
        feedback += f"Flagged phrases: {', '.join(flagged[:3])}. "
    
    # Add local similarity feedback
    local_similarity = checks.get("local_similarity", {})
    similarity_score = local_similarity.get("similarity_score", 0)
    if similarity_score > 20:
        feedback += f"High similarity ({similarity_score}%) with previous content. "

    if needs_rewrite:
        return state.update(
            plagiarism_feedback=feedback,
            needs_rewrite=True,
            next_action="rewrite_section",
        )
    else:
        # Advance to next section if available; otherwise complete
        sections = state.sections or []
        current_id = state.current_section.get("id") if state.current_section else None
        next_section = None
        for idx, s in enumerate(sections):
            if s.get("id") == current_id:
                if idx + 1 < len(sections):
                    next_section = sections[idx + 1]
                break
        if next_section:
            return state.update(current_section=next_section, next_action="draft_section")
        else:
            return state.update(next_action="completion")


def rewrite_section_node(state: EnhancedBlogState) -> EnhancedBlogState:
    """Plagiarism-aware content revision with detailed guidance"""
    if not state.current_section:
        return state.update(next_action="completion")

    section_id = state.current_section["id"]
    original = state.section_drafts.get(section_id, "")
    feedback = state.plagiarism_feedback or ""
    
    # Get detailed plagiarism analysis for better guidance
    checks = state.plagiarism_checks.get(section_id, {})
    ai_analysis = checks.get("ai", {})
    local_similarity = checks.get("local_similarity", {})
    
    # Create detailed rewrite instructions
    rewrite_instructions = _generate_rewrite_instructions(original, feedback, ai_analysis, local_similarity)

    prompt = f"""
You are a technical writer tasked with revising content to eliminate plagiarism while maintaining accuracy and quality.

### ORIGINAL CONTENT:
{original[:3000]}

### REVISION INSTRUCTIONS:
{rewrite_instructions}

### REQUIREMENTS:
1. Maintain all technical accuracy and key information
2. Use completely original phrasing and sentence structures
3. Add appropriate citations for any factual claims
4. Ensure the revised content flows naturally
5. Address all specific issues identified above

### OUTPUT ONLY THE REVISED CONTENT:
"""

    writer_llm = local_llm_manager.get_writer()
    response = writer_llm.invoke([
        ("system", "You are an expert technical writer skilled in plagiarism prevention and content revision."),
        ("human", prompt)
    ])
    updated_state = track_token_usage(state, response)

    # Update revision history
    updated_history = updated_state.revision_history.copy()
    section_history = updated_history.get(section_id, [])
    section_history.append({
        "original": original[:500] + "..." if len(original) > 500 else original,
        "revised": response.content,
        "feedback": feedback,
        "timestamp": __import__('time').time()
    })
    updated_history[section_id] = section_history

    # Update section draft
    updated_drafts = updated_state.section_drafts.copy()
    updated_drafts[section_id] = response.content

    return updated_state.update(
        section_drafts=updated_drafts,
        revision_history=updated_history,
        needs_rewrite=False,
        next_action="plagiarism_check",  # Re-check
    )


def should_check_content(state: EnhancedBlogState, content: str) -> bool:
    """Heuristics to conserve API credits"""
    if state.free_tier_credits <= 0:
        return False
    if len(content.split()) < 150:
        return False
    code_keywords = ["def ", "class ", "import ", "function ", "{", "}"]
    if any(kw in content for kw in code_keywords):
        return False
    return True


def _quick_similarity_check(content: str, state: EnhancedBlogState) -> Dict[str, Any]:
    """Quick local similarity check using n-gram analysis"""
    try:
        # Get all previous section contents
        previous_contents = []
        for section_id, draft in state.section_drafts.items():
            if section_id != (state.current_section or {}).get("id"):
                previous_contents.append(draft)
        
        if not previous_contents:
            return {"similarity_score": 0, "detailed_analysis": "No previous content to compare"}
        
        # Simple n-gram similarity
        content_words = content.lower().split()
        max_similarity = 0
        
        for prev_content in previous_contents:
            prev_words = prev_content.lower().split()
            # Calculate overlap
            overlap = len(set(content_words) & set(prev_words))
            union = len(set(content_words) | set(prev_words))
            if union > 0:
                similarity = (overlap / union) * 100
                max_similarity = max(max_similarity, similarity)
        
        return {
            "similarity_score": round(max_similarity, 2),
            "detailed_analysis": f"Maximum similarity with previous sections: {max_similarity:.2f}%"
        }
    except Exception as e:
        return {
            "similarity_score": 0,
            "detailed_analysis": f"Similarity check failed: {str(e)}"
        }


def _should_use_api_check(ai_result: Dict, local_similarity: Dict) -> bool:
    """Determine if API check is needed based on local analysis"""
    # Use API if AI risk score is high
    ai_risk = ai_result.get("risk_score", 0)
    if ai_risk > 50:
        return True
    
    # Use API if local similarity is high
    similarity_score = local_similarity.get("similarity_score", 0)
    if similarity_score > 20:
        return True
    
    # Use API if there are many flagged phrases
    flagged_phrases = ai_result.get("flagged_phrases", [])
    if len(flagged_phrases) > 5:
        return True
    
    # Otherwise, rely on local analysis
    return False


def _estimate_plagiarism_score(ai_result: Dict, local_similarity: Dict) -> int:
    """Estimate plagiarism score based on local analysis"""
    # Weighted combination of factors
    ai_risk = ai_result.get("risk_score", 0) * 0.6
    similarity = local_similarity.get("similarity_score", 0) * 0.3
    flagged_count = min(len(ai_result.get("flagged_phrases", [])), 10) * 2  # Max 20 points for flagged phrases
    
    estimated_score = (ai_risk + similarity + flagged_count) / 2  # Scale down
    return min(100, max(0, int(estimated_score)))


def _estimate_api_score(content: str, ai_result: Dict, local_similarity: Dict) -> int:
    """Estimate API score (in practice, this would call the actual API)"""
    # For now, we'll simulate this with a more sophisticated estimate
    # In practice, this would be replaced with actual API call
    estimated = _estimate_plagiarism_score(ai_result, local_similarity)
    # Add some randomness to simulate API variance
    import random
    return max(0, min(100, estimated + random.randint(-10, 10)))


def _get_plagiarism_score(checks: Dict) -> int:
    """Get plagiarism score from any available source"""
    # Priority: API > Estimated > Default to 0
    if "api" in checks:
        return checks["api"].get("score", 0)
    elif "estimated" in checks:
        return checks["estimated"].get("score", 0)
    else:
        # Fallback to AI risk score if no other scores available
        ai_result = checks.get("ai", {})
        # Scale AI risk score (0-100) to plagiarism score (0-100)
        return int(ai_result.get("risk_score", 0) * 0.8)


def _generate_rewrite_instructions(original: str, feedback: str, ai_analysis: Dict, local_similarity: Dict) -> str:
    """Generate detailed rewrite instructions based on plagiarism analysis"""
    instructions = []
    
    # Add general feedback
    if feedback:
        instructions.append(f"ADDRESS THE FOLLOWING ISSUES:\n{feedback}")
    
    # Add AI analysis guidance
    ai_risk = ai_analysis.get("risk_score", 0)
    if ai_risk > 50:
        instructions.append("HIGH PLAGIARISM RISK DETECTED - COMPLETE REWRITING REQUIRED")
        
    flagged_phrases = ai_analysis.get("flagged_phrases", [])
    if flagged_phrases:
        instructions.append(f"AVOID THESE PHRASES: {', '.join(flagged_phrases[:5])}")
    
    # Add similarity guidance
    similarity_score = local_similarity.get("similarity_score", 0)
    if similarity_score > 20:
        instructions.append(f"REDUCE SIMILARITY WITH PREVIOUS CONTENT (currently {similarity_score}%)")
        instructions.append("Use different vocabulary and sentence structures")
    
    # Add general rewriting strategies
    instructions.extend([
        "REWRITING STRATEGIES:",
        "1. Change sentence structure (active/passive, complex/simple)",
        "2. Use synonyms and alternative expressions",
        "3. Rearrange paragraphs and ideas",
        "4. Add original examples and explanations",
        "5. Include proper citations for factual information",
        "6. Break up long similar passages with your own analysis",
        "7. Use transition words to improve flow with original language"
    ])
    
    # Add content-specific guidance
    if len(original.split()) > 500:
        instructions.append("8. Focus on the sections with highest similarity first")
    
    return "\n\n".join(instructions)
