"""Modules for interacting with AI models (LLMs, Plagiarism APIs, etc.)."""

import logging

from .llm_manager import local_llm_manager
from .plagiarism import plagiarism_detector
from .summarizer import summarizer

# Define the public API of the models package
__all__ = ["LocalLLMManager", "PlagiarismDetector", "HybridSummarizer"]

# Package-level logger
log = logging.getLogger(__name__)