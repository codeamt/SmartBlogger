from langchain_community.retrievers import ArxivRetriever
from models.summarizer import summarizer
from ...state import EnhancedBlogState


def execute_arxiv_search(query: str, state: EnhancedBlogState) -> list:
    """Search arXiv and return a list of structured results for a single query."""
    try:
        arxiv = ArxivRetriever(load_max_docs=3)
        docs = arxiv.get_relevant_documents(query=query)
        results = []
        for doc in docs:
            try:
                summary = summarizer.summarize(
                    content=doc.page_content,
                    query=query,
                    state=state.dict() if hasattr(state, "dict") else {}
                )
            except Exception:
                summary = doc.page_content[:300] + "..."
            results.append({
                "title": doc.metadata.get("Title") or doc.metadata.get("title", "arXiv paper"),
                "url": doc.metadata.get("Entry ID") or doc.metadata.get("entry_id", ""),
                "content": doc.page_content[:500],
                "summary": summary,
                "authors": doc.metadata.get("Authors", []),
                "published": doc.metadata.get("Published", "")
            })
        return results
    except Exception as e:
        print(f"Arxiv processing error: {e}")
        return []