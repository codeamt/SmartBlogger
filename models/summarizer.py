import os
import logging
from typing import Optional
from transformers import pipeline
from .llm_manager import local_llm_manager
from config import SummarizationConfig

# Logger for the module
log = logging.getLogger(__name__)

# Simple in-module cache to avoid import errors if external caching is not available
_SUMMARY_CACHE = {}

def get_cached_summary(content: str, query: str):
    key = (hash(content), query)
    return _SUMMARY_CACHE.get(key)

def set_cached_summary(content: str, query: str, summary: str):
    key = (hash(content), query)
    _SUMMARY_CACHE[key] = summary


class HybridSummarizer:
    def __init__(self):
        self.hf_model = None
        self.local_llm = local_llm_manager.get_researcher()
        self.fast_local_llm = local_llm_manager.get_writer()
        # Load thresholds from config
        self.fast_threshold = getattr(SummarizationConfig, 'FAST_THRESHOLD', 800)
        self.llm_threshold = getattr(SummarizationConfig, 'LLM_THRESHOLD', 1500)

    def _initialize_hf_model(self):
        """Lazy load HF model to avoid slow startup"""
        if self.hf_model is None:
            try:
                self.hf_model = pipeline(
                    "summarization",
                    model="facebook/bart-large-cnn",  # Fixed model name
                    device=-1  # Use CPU (better for Apple Silicon compatibility)
                )
            except Exception as e:
                print(f"Warning: Could not load HF summarization model: {e}")
                self.hf_model = None

    def summarize(self, content: str, query: str, state: dict) -> str:
        """Smart summarization using local resources"""
        # Check cache first
        cached = get_cached_summary(content, query)
        if cached:
            return cached

        # Choose summarization method based on content length and available resources
        # Fixed logic: use fast model for very short text, LLM for medium, chunking for long
        if len(content) < self.fast_threshold:
            summary = self._fast_summarize(content, query)
        elif len(content) < self.llm_threshold:
            summary = self._local_llm_summarize(content, query, state)
        else:
            # For very long content, use chunking strategy
            summary = self._chunked_summarize(content, query, state)

        # Cache result
        set_cached_summary(content, query, summary)
        return summary

    def _fast_summarize(self, content: str, query: str) -> str:
        """Fast summarization for short content using HF or simple extraction"""
        try:
            # Try HF model first
            self._initialize_hf_model()  # FIXED: self_initialize -> self._initialize
            if self.hf_model is not None:
                summary = self.hf_model(
                    f"Relevant to '{query}': {content[:1024]}",
                    max_length=150,
                    min_length=50,
                    do_sample=False
                )[0]['summary_text']
                return summary
        except Exception as e:
            print(f"HF summarization failed: {e}")  # FIXED: printf -> print

        # Fallback: simple extraction-based summarization
        return self._extractive_summarize(content, query)

    def _extractive_summarize(self, content: str, query: str) -> str:
        """Simple extractive summarization as fallback"""
        sentences = content.split('. ')
        if len(sentences) <= 3:
            return content[:500] + "..."

        # Simple heuristic: take first, middle, and last sentences
        important_sentences = [
            sentences[0],
            sentences[len(sentences) // 2],
            sentences[-1]
        ]

        summary = '. '.join(important_sentences) + '.'
        return summary[:500] + "..." if len(summary) > 500 else summary

    def _local_llm_summarize(self, content: str, query: str, state: dict) -> str:
        """High-quality summarization using local LLM"""
        prompt = f"""
        Create a concise technical summary relevant to '{query}':

        CONTENT:
        {content[:6000]}

        Instructions:
        - Focus on key technical concepts and findings
        - Maintain accuracy and technical precision
        - Keep summary under 200 words
        - Extract the most relevant information for technical blog research
        - Use clear, concise language
        """

        try:
            response = self.local_llm.invoke([
                ("system",
                 "You are a technical research assistant. Create accurate, concise summaries focusing on key technical insights."),
                ("human", prompt)
            ])

            # Token usage is now handled by the LLM manager
            # The response should already contain token usage information
            return response.content.strip()

        except Exception as e:
            print(f"Local LLM summarization failed: {e}")
            return self._extractive_summarize(content, query)

    def _chunked_summarize(self, content: str, query: str, state: dict) -> str:
        """Handle very long content by summarizing in chunks"""
        chunk_size = 4000
        chunks = [content[i:i + chunk_size] for i in range(0, len(content), chunk_size)]

        if len(chunks) == 1:
            return self._local_llm_summarize(content, query, state)

        # Summarize each chunk
        chunk_summaries = []
        for i, chunk in enumerate(chunks[:3]):  # Limit to first 3 chunks to avoid excessive processing
            chunk_summary = self._fast_summarize(chunk, query)
            chunk_summaries.append(f"Part {i + 1}: {chunk_summary}")

        # Combine chunk summaries
        combined_summaries = "\n\n".join(chunk_summaries)

        # Create final summary from chunk summaries
        final_prompt = f"""
        Combine these partial summaries into one coherent technical summary relevant to '{query}':

        PARTIAL SUMMARIES:
        {combined_summaries}

        Create a unified summary that captures the main technical points.
        """

        try:
            response = self.local_llm.invoke([
                ("system", "You are a technical editor. Combine partial summaries into a coherent whole."),
                ("human", final_prompt)
            ])

            # Token usage is now handled by the LLM manager
            # The response should already contain token usage information
            return response.content.strip()

        except Exception as e:
            print(f"Chunked summarization failed: {e}")
            return combined_summaries[:1000] + "..."


# The _track_token_usage method is no longer needed as token tracking is handled by the LLM manager
# This method can be removed in a future refactoring

    def summarize_research_results(self, research_context: dict, query: str, state: dict) -> dict:
        """Summarize entire research context for drafting"""
        summarized_research = {}

        for source, results in research_context.items():
            if not results:
                continue

            if source == "arxiv":
                # Arxiv papers already have summaries
                summarized_research[source] = results
            elif source == "web":
                summarized_research[source] = self._summarize_web_results(results, query, state)
            elif source == "documents":
                summarized_research[source] = self._summarize_document_results(results, query, state)
            else:
                summarized_research[source] = results

        return summarized_research

    def _summarize_web_results(self, web_results: list, query: str, state: dict) -> list:
        """Summarize web search results"""
        summarized = []

        for result in web_results[:5]:  # Limit to top 5
            content = result.get('content', '') or result.get('snippet', '')
            if len(content) > 300:
                summary = self.summarize(content, query, state)
                summarized.append({
                    **result,
                    'content_summary': summary,
                    'original_length': len(content)
                })
            else:
                summarized.append({**result, 'content_summary': content})

        return summarized

    def _summarize_document_results(self, doc_results: list, query: str, state: dict) -> list:
        """Summarize document search results"""
        summarized = []

        for doc in doc_results[:5]:  # Limit to top 5
            content = doc.get('text', '') or doc.get('content', '')
            if len(content) > 400:
                summary = self.summarize(content, query, state)
                summarized.append({
                    **doc,
                    'text_summary': summary,
                    'original_length': len(content)
                })
            else:
                summarized.append({**doc, 'text_summary': content})

        return summarized


# Global instance
summarizer = HybridSummarizer()