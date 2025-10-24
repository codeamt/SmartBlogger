from ..state import EnhancedBlogState
from ..utils.token_tracking import track_token_usage
from models.plagiarism import plagiarism_detector
from models.llm_manager import llm_manager
import random


def plagiarism_check_node(state: EnhancedBlogState) -> EnhancedBlogState:
    """Smart plagiarism detection"""
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

    # AI plagiarism analysis
    ai_result = plagiarism_detector.analyze_content(content, updated_fingerprints)

    # Initialize results
    results = {'ai': ai_result}

    # Should we do API check?
    if should_check_content(state, content):
        # Simulated API response (replace with actual Copyleaks call)
        results["api"] = {"score": random.randint(0, 30)}
        updated_credits = state.free_tier_credits - 1
    else:
        updated_credits = state.free_tier_credits

    # Update plagiarism checks
    updated_checks = state.plagiarism_checks.copy()
    updated_checks[section_id] = results

    return state.update(
        content_fingerprints=updated_fingerprints,
        plagiarism_checks=updated_checks,
        free_tier_credits=updated_credits,
        next_action="evaluate_plagiarism"
    )


def evaluate_plagiarism_node(state: EnhancedBlogState) -> EnhancedBlogState:
    """Evaluate plagiarism results and decide if rewriting is needed"""
    if not state.current_section:
        return state.update(next_action="completion")

    section_id = state.current_section["id"]
    checks = state.plagiarism_checks.get(section_id, {})

    needs_rewrite = False
    feedback = ""

    # Check API results
    if "api" in checks and checks["api"].get("score", 0) > 15:  # Use your PLAGIARISM_THRESHOLD
        needs_rewrite = True
        feedback += f"API similarity score {checks['api']['score']}% exceeds threshold. "

    # Check AI analysis
    if "ai" in checks and checks["ai"].get("risk_score", 0) > 70:
        needs_rewrite = True
        feedback += f"High AI risk score {checks['ai']['risk_score']}/100. "

    if checks.get("ai", {}).get("flagged_phrases"):
        feedback += f"Flagged phrases: {', '.join(checks['ai']['flagged_phrases'][:3])}. "

    if needs_rewrite:
        return state.update(
            plagiarism_feedback=feedback,
            needs_rewrite=True,
            next_action="rewrite_section"
        )
    else:
        return state.update(next_action="completion")


def rewrite_section_node(state: EnhancedBlogState) -> EnhancedBlogState:
    """Plagiarism-aware content revision"""
    if not state.current_section:
        return state.update(next_action="completion")

    section_id = state.current_section["id"]
    original = state.section_drafts.get(section_id, "")
    feedback = state.plagiarism_feedback or ""

    prompt = f"""
    ### REVISION REQUEST: Plagiarism Prevention
    ### Original Content:
    {original[:2000]}

    ### Issues Found:
    {feedback}

    ### Rewrite Instructions:
    1. Paraphrase using original wording
    2. Add citations where needed
    3. Change sentence structures
    4. Maintain technical accuracy
    5. Keep the same core information
    """

    writer_llm = llm_manager.get_writer()
    response = writer_llm.invoke(prompt)
    updated_state = track_token_usage(state, response)

    # Update revision history
    updated_history = state.revision_history.copy()
    section_history = updated_history.get(section_id, [])
    section_history.append(response.content)
    updated_history[section_id] = section_history

    # Update section draft
    updated_drafts = state.section_drafts.copy()
    updated_drafts[section_id] = response.content

    return updated_state.update(
        section_drafts=updated_drafts,
        revision_history=updated_history,
        needs_rewrite=False,
        next_action="plagiarism_check"  # Re-check
    )


def should_check_content(state: EnhancedBlogState, content: str) -> bool:
    """Heuristics to conserve API credits"""
    # Skip if no credits
    if state.free_tier_credits <= 0:
        return False

    # Skip short sections
    if len(content.split()) < 150:
        return False

    # Skip code-heavy content
    code_keywords = ["def ", "class ", "import ", "function ", "{", "}"]
    if any(kw in content for kw in code_keywords):
        return False

    return True