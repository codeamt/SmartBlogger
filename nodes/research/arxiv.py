from models.summarizer import summarizer
from state import EnhancedBlogState


def execute_arxiv_search(query: str, state: EnhancedBlogState) -> list:
    """Search arXiv via the arxiv package and return normalized results."""
    try:
        import arxiv  # lightweight client
    except Exception as e:
        print(f"Arxiv package not available: {e}")
        return []

    try:
        search = arxiv.Search(query=query, max_results=3, sort_by=arxiv.SortCriterion.Relevance)
        results = []
        for result in search.results():
            try:
                abstract = result.summary or ""
                summary = summarizer.summarize(
                    content=abstract,
                    query=query,
                    state=state.dict() if hasattr(state, "dict") else {}
                )
            except Exception:
                summary = (result.summary or "")[:300] + "..."

            authors = [a.name for a in (result.authors or [])]
            published = getattr(result, "published", None)
            url = getattr(result, "entry_id", None) or getattr(result, "pdf_url", None) or ""

            results.append({
                "title": getattr(result, "title", None) or "arXiv paper",
                "url": url,
                "content": (result.summary or "")[:500],
                "summary": summary,
                "authors": authors,
                "published": str(published) if published else ""
            })
        return results
    except Exception as e:
        print(f"Arxiv processing error: {e}")
        return []