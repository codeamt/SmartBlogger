from langchain_community.retrievers import ArxivRetriever
from models.summarizer import summarizer
from state import EnhancedBlogState


def arxiv_research_node(state: EnhancedBlogState) -> EnhancedBlogState:
    if not state.get("research_queries"):
        return state

    arxiv = ArxivRetriever(load_max_docs=3)
    results = []

    for query in state["research_queries"]:
        try:
            docs = arxiv.get_relevant_documents(query=query)
            for doc in docs:
                summary = summarizer.summarize(
                    content=doc.page_content,
                    query=query,
                    state=state
                )

                results.append({
                    "title": doc.metadata["Title"],
                    "url": doc.metadata["Entry ID"],
                    "summary": summary,
                    "authors": doc.metadata["Authors"],
                    "published": doc.metadata["Published"]
                })
        except Exception as e:
            print(f"Arxiv processing error: {e}")

    return {
        **state,
        "research_context": {
            **state.get("research_context", {}),
            "arxiv": results
        }
    }