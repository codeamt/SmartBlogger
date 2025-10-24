from typing import Dict


def track_token_usage(state, response):
    """Update state's token usage from a model response if available."""
    usage: Dict[str, int] = getattr(state, "token_usage", {}) or {}
    metadata = getattr(response, "response_metadata", {}) or {}
    tokens = metadata.get("token_usage", {})

    # Merge counts
    for k in ("prompt_tokens", "completion_tokens", "total_tokens"):
        if k in tokens:
            usage[k] = usage.get(k, 0) + int(tokens.get(k, 0))

    return state.update(token_usage=usage)
