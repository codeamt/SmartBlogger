import os
import requests
import json
from typing import Dict, List, Any
from models.summarizer import summarizer
from state import EnhancedBlogState
from config import EMERGENTMIND_API_KEY, EMERGENTMIND_DAILY_LIMIT


# Global variable to track daily usage
_emergentmind_usage_count = 0


def execute_arxiv_search(query: str, state: EnhancedBlogState) -> list:
    """Enhanced arXiv search with EmergentMind API integration and fallback to traditional search."""
    # Try EmergentMind API first if available and within limits
    if _should_use_emergentmind():
        emergent_results = _search_emergentmind_arxiv(query, state)
        if emergent_results:
            global _emergentmind_usage_count
            _emergentmind_usage_count += 1
            return emergent_results
    
    # Fallback to traditional arxiv search
    return _search_traditional_arxiv(query, state)


def _should_use_emergentmind() -> bool:
    """Check if we should use EmergentMind API based on availability and usage limits."""
    global _emergentmind_usage_count
    return (
        bool(EMERGENTMIND_API_KEY) and 
        _emergentmind_usage_count < EMERGENTMIND_DAILY_LIMIT
    )


def _search_emergentmind_arxiv(query: str, state: EnhancedBlogState) -> list:
    """Search arXiv via EmergentMind API for enhanced results."""
    try:
        url = "https://api.emergentmind.com/v1/papers/search"
        headers = {
            "Authorization": f"Bearer {EMERGENTMIND_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Enhanced query for better results
        enhanced_query = _generate_enhanced_arxiv_query(query)
        
        payload = {
            "query": enhanced_query,
            "limit": 5,  # Get more results for better filtering
            "sort": "relevance",
            "filters": {
                "published_after": "2022-01-01",  # Focus on recent papers
                "min_citations": 10  # Filter for papers with some impact
            }
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            papers = data.get("papers", [])
            
            # Process and enhance results
            results = []
            for paper in papers[:3]:  # Limit to top 3 results
                enhanced_paper = _enhance_emergentmind_paper(paper, query, state)
                results.append(enhanced_paper)
            
            return results
        else:
            print(f"EmergentMind API error: {response.status_code} - {response.text}")
            return []
            
    except Exception as e:
        print(f"EmergentMind search error: {e}")
        return []


def _generate_enhanced_arxiv_query(query: str) -> str:
    """Generate an enhanced query for better paper discovery."""
    # Add context to make the query more specific and valuable
    return f"{query} high-impact research paper with significant citations and practical applications"


def _enhance_emergentmind_paper(paper: Dict, query: str, state: EnhancedBlogState) -> Dict:
    """Enhance EmergentMind paper data with additional processing."""
    try:
        # Extract key information
        title = paper.get("title", "Research Paper")
        abstract = paper.get("abstract", "")
        authors = paper.get("authors", [])
        
        # Create enhanced summary
        summary = summarizer.summarize(
            content=abstract,
            query=query,
            state=state.dict() if hasattr(state, "dict") else {}
        )
        
        # Extract additional metadata
        enhanced_metadata = _extract_paper_metadata(paper)
        
        return {
            "title": title,
            "url": paper.get("url", ""),
            "content": abstract[:800] + ("..." if len(abstract) > 800 else ""),
            "summary": summary,
            "authors": [author.get("name", "") for author in authors[:3]],
            "published": paper.get("published_date", ""),
            "type": "arxiv_emergentmind",
            "metadata": enhanced_metadata,
            "quality_score": _calculate_paper_quality_score(paper)
        }
        
    except Exception as e:
        print(f"Error enhancing paper: {e}")
        # Fallback to basic paper data
        return {
            "title": paper.get("title", "Research Paper"),
            "url": paper.get("url", ""),
            "content": paper.get("abstract", "")[:500],
            "summary": (paper.get("abstract", "")[:300] + "..."),
            "authors": [author.get("name", "") for author in paper.get("authors", [])[:3]],
            "published": paper.get("published_date", ""),
            "type": "arxiv_emergentmind"
        }


def _extract_paper_metadata(paper: Dict) -> Dict:
    """Extract additional metadata from paper data."""
    return {
        "citation_count": paper.get("citation_count", 0),
        "influential_citation_count": paper.get("influential_citation_count", 0),
        "reference_count": paper.get("reference_count", 0),
        "venue": paper.get("venue", ""),
        "year": paper.get("year", 0),
        "topics": paper.get("topics", []),
        "key_contributions": paper.get("key_contributions", []),
        "methodologies": paper.get("methodologies", [])
    }


def _calculate_paper_quality_score(paper: Dict) -> int:
    """Calculate a quality score for the paper (0-100)."""
    score = 50  # Base score
    
    # Citation scoring
    citations = paper.get("citation_count", 0)
    if citations >= 100:
        score += 30
    elif citations >= 50:
        score += 20
    elif citations >= 10:
        score += 10
    
    # Year scoring (prefer recent papers)
    year = paper.get("year", 0)
    if 2023 <= year <= 2024:
        score += 15
    elif 2021 <= year <= 2022:
        score += 10
    
    # Venue scoring (if available)
    venue = paper.get("venue", "").lower()
    high_quality_venues = ["nature", "science", "cell", "neurips", "icml", "cvpr", "acl"]
    if any(venue_name in venue for venue_name in high_quality_venues):
        score += 15
    
    # Author count (more authors might indicate collaboration)
    author_count = len(paper.get("authors", []))
    if 2 <= author_count <= 6:
        score += 5
    
    return min(100, max(0, score))


def _search_traditional_arxiv(query: str, state: EnhancedBlogState) -> list:
    """Traditional arXiv search as fallback."""
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
                "published": str(published) if published else "",
                "type": "arxiv_traditional"
            })
        return results
    except Exception as e:
        print(f"Arxiv processing error: {e}")
        return []