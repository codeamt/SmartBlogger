from typing import Dict, List

def format_research_for_drafting(research_context: Dict, current_section: Dict) -> str:
    """Format research specifically for the current section"""
    if not research_context:
        return "No research context available"

    section_title = current_section.get('title', '').lower()
    formatted = "## Research Insights for Section\n\n"

    # Smart filtering based on section content
    relevant_insights = filter_research_by_section(research_context, section_title)

    if not relevant_insights:
        return "No directly relevant research found for this section."

    # Format by relevance
    formatted += "### Most Relevant Sources:\n"

    for source_type, insights in relevant_insights.items():
        if insights:
            formatted += f"\n#### {source_type.upper()}:\n"
            for i, insight in enumerate(insights[:2], 1):  # Top 2 per source
                formatted += f"{i}. **{insight.get('title', 'Source')}**\n"
                formatted += f"   {insight.get('content', '')[:150]}...\n"
                if insight.get('url'):
                    formatted += f"   [Read more]({insight['url']})\n"
                formatted += "\n"

    return formatted


def filter_research_by_section(research_context: Dict, section_title: str) -> Dict:
    """Filter research to show only what's relevant to current section"""
    filtered = {}

    keywords = extract_keywords(section_title)

    for source_type, results in research_context.get('by_source', {}).items():
        relevant_results = []
        for result in results:
            if is_relevant_to_section(result, keywords):
                relevant_results.append(result)
        if relevant_results:
            filtered[source_type] = relevant_results

    return filtered


def extract_keywords(section_title: str) -> List[str]:
    """Extract keywords from section title for relevance matching"""
    common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
    words = section_title.lower().split()
    return [word for word in words if word not in common_words and len(word) > 2]


def is_relevant_to_section(result: Dict, keywords: List[str]) -> bool:
    """Check if a research result is relevant to the current section"""
    content = f"{result.get('title', '')} {result.get('content', '')}".lower()
    return any(keyword in content for keyword in keywords)