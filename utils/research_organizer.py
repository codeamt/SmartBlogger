from typing import Dict, List
# from models.summarizer import summarizer


def organize_research_results(all_results: Dict) -> Dict:
    """Organize research results by source for optimal consumption"""
    organized = {
        "by_source": {},
        "by_topic": {},
        "key_insights": [],
        "citations": []
    }

    for query, sources in all_results.items():
        organized["by_topic"][query] = sources

        for source_name, results in sources.items():
            if source_name not in organized["by_source"]:
                organized["by_source"][source_name] = []

            organized["by_source"][source_name].extend(results)

            # Extract key insights and citations
            for result in results[:3]:  # Top 3 results per source
                if source_name == "arxiv" and "title" in result:
                    organized["citations"].append({
                        "type": "academic",
                        "title": result["title"],
                        "url": result["url"],
                        "authors": result.get("authors", []),
                        "year": extract_year(result.get("published", ""))
                    })
                elif "url" in result:
                    organized["citations"].append({
                        "type": "web",
                        "title": result.get("title", "Source"),
                        "url": result["url"],
                        "snippet": result.get("content", "")[:100]
                    })

    # Deduplicate citations
    organized["citations"] = deduplicate_citations(organized["citations"])

    return organized


def deduplicate_citations(citations: List[Dict]) -> List[Dict]:
    """Remove duplicate citations based on URL"""
    seen_urls = set()
    unique_citations = []

    for citation in citations:
        url = citation.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_citations.append(citation)

    return unique_citations


def extract_year(date_string: str) -> str:
    """Extract year from date string"""
    import re
    year_match = re.search(r'\d{4}', date_string)
    return year_match.group() if year_match else "Unknown"