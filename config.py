import os
from typing import Dict, Any


# Local LLM settings
class ModelConfig:
    LOCAL_WRITER_MODEL = os.getenv("LOCAL_WRITER_MODEL", "llama3.1:8b")
    LOCAL_RESEARCHER_MODEL = os.getenv("LOCAL_RESEARCHER_MODEL", "llama3.1:8b")
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    # Fallback to Groq if local not available (optional)
    GROQ_WRITER = "llama3-70b-8192"
    GROQ_RESEARCHER = "mixtral-8x7b-32768"


# - Add summarization settings
class SummarizationConfig:
    MAX_CONTENT_LENGTH = 30000
    CHUNK_SIZE = 4000
    HF_MODEL = "facebook/bart-large-cnn"  # Fallback model
    ENABLE_HF_FALLBACK = True  # Set to False if you want pure local LLM only


# ADD VALIDATION
def validate_environment() -> Dict[str, Any]:
    """Validate all required environment variables and dependencies"""
    issues = []
    warnings = []

    # Check local LLM availability
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            issues.append("Ollama not running on localhost:11434")
    except:
        issues.append("Cannot connect to Ollama. Please ensure it's installed and running.")

    # Check required APIs
    if not os.getenv("TAVILY_API_KEY") and not os.getenv("PERPLEXITY_API_KEY"):
        warnings.append("No web search API configured. Research capabilities will be limited.")

    # Check plagiarism threshold
    plagiarism_threshold = int(os.getenv("PLAGIARISM_THRESHOLD", 15))
    if plagiarism_threshold < 5 or plagiarism_threshold > 50:
        issues.append(f"PLAGIARISM_THRESHOLD should be between 5 and 50, got {plagiarism_threshold}")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings
    }


# Add to config.py
VALIDATION_RESULT = validate_environment()

# Other configurations remain the same
PLAGIARISM_THRESHOLD = int(os.getenv("PLAGIARISM_THRESHOLD", 15))
FREE_TIER_CREDITS = int(os.getenv("FREE_TIER_CREDITS", 100))