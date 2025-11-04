import os
import requests
import json
import re
from typing import Dict, List, Any
from .perplexity import execute_perplexity_search
from models.llm_manager import local_llm_manager


def execute_substack_search(query: str, state=None) -> list:
    """Enhanced Substack search with comprehensive analysis via Perplexity"""
    try:
        # Use comprehensive query template for better results
        comprehensive_query = _generate_comprehensive_substack_query(query)
        site_query = f"site:substack.com {comprehensive_query}"
        
        # Execute search
        results = execute_perplexity_search(site_query, state)
        
        # Enhance results with quality analysis
        enhanced_results = _analyze_substack_quality(results, state)
        
        return enhanced_results
    except Exception as e:
        print(f"Substack search error: {e}")
        return []


def substack_api_search(query: str, api_key: str) -> list:
    """Search Substack using official API with enhanced metadata"""
    headers = {"Authorization": f"Bearer {api_key}"}
    search_url = f"https://api.substack.com/v1/search/posts?query={query}&limit=5"

    response = requests.get(search_url, headers=headers, timeout=15)
    if response.status_code == 200:
        data = response.json()
        results = []

        for post in data.get('posts', [])[:5]:
            # Extract additional metadata
            engagement_metrics = _extract_engagement_metrics(post)
            content_analysis = _analyze_content_quality(post)
            
            results.append({
                "title": post.get('title', ''),
                "url": post.get('canonical_url', ''),
                "content": post.get('description', '')[:300] + "...",
                "author": post.get('author', {}).get('name', ''),
                "published": post.get('post_date', ''),
                "subscriber_count": post.get('subscriber_count', 0),
                "engagement": engagement_metrics,
                "content_quality": content_analysis,
                "type": "substack_post"
            })

        return results
    return []


def substack_web_search(query: str) -> list:
    """Enhanced fallback web search for Substack with quality analysis"""
    try:
        # Try multiple approaches for better coverage
        search_urls = [
            f"https://substack.com/api/v1/search/posts?query={query}",
            f"https://www.google.com/search?q=site:substack.com+{query}"
        ]
        
        for search_url in search_urls:
            try:
                response = requests.get(search_url, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    results = []

                    for post in data.get('posts', [])[:5]:
                        # Enhanced post analysis
                        enhanced_post = _enhance_substack_post(post, query)
                        results.append(enhanced_post)

                    return results
            except:
                continue
    except Exception as e:
        print(f"Substack web search error: {e}")
        pass

    return []  # Return empty if no Substack access


def _generate_comprehensive_substack_query(topic: str) -> str:
    """Generate a comprehensive query for Substack analysis"""
    return f"""
    Find high-quality Substack content about "{topic}" and analyze:
    
    1. POPULAR POSTS: Most engaging recent posts (last 12 months) with subscriber growth
    2. EXPERT NEWSLETTERS: Publications with 5000+ subscribers offering in-depth analysis
    3. BEGINNER-FRIENDLY: Posts that effectively explain "{topic}" to newcomers with clear examples
    4. CONTENT STRUCTURE: Newsletters with excellent narrative flow and reader retention techniques
    5. SUCCESS METRICS: Examples with strong subscriber retention or monetization strategies
    
    For each result, provide:
    - Newsletter name and author
    - Subscriber count estimate
    - Key content strengths
    - Notable writing techniques
    - Engagement indicators (comments, shares, viral status)
    - Unique value proposition
    
    Focus on content that demonstrates expertise while remaining accessible.
    """


def _analyze_substack_quality(results: list, state=None) -> list:
    """Analyze Substack results for quality metrics"""
    enhanced_results = []
    
    for result in results:
        # Add quality analysis
        quality_score = _calculate_substack_quality_score(result)
        content_insights = _extract_content_insights(result)
        
        enhanced_result = result.copy()
        enhanced_result.update({
            "quality_score": quality_score,
            "content_insights": content_insights,
            "type": "substack_analysis"
        })
        
        enhanced_results.append(enhanced_result)
    
    # Sort by quality score
    enhanced_results.sort(key=lambda x: x.get("quality_score", 0), reverse=True)
    return enhanced_results[:5]  # Return top 5 results


def _calculate_substack_quality_score(result: Dict) -> int:
    """Calculate a quality score for Substack content (0-100)"""
    score = 50  # Base score
    
    content = result.get("content", "")
    title = result.get("title", "")
    
    # Length scoring (500-1500 words is ideal)
    word_count = len(content.split())
    if 500 <= word_count <= 1500:
        score += 20
    elif word_count > 1500:
        score += 10
    
    # Title quality (indicates clear focus)
    if len(title.split()) >= 3 and len(title.split()) <= 10:
        score += 10
    
    # Engagement indicators in content
    engagement_keywords = ["subscribers", "engagement", "comments", "shares", "viral"]
    engagement_count = sum(1 for keyword in engagement_keywords if keyword in content.lower())
    score += min(engagement_count * 5, 15)
    
    # Quality indicators
    quality_keywords = ["expert", "in-depth", "comprehensive", "analysis", "research"]
    quality_count = sum(1 for keyword in quality_keywords if keyword in content.lower())
    score += min(quality_count * 3, 15)
    
    return min(100, max(0, score))


def _extract_content_insights(result: Dict) -> Dict:
    """Extract content insights from Substack posts"""
    content = result.get("content", "")
    
    # Extract potential insights using simple pattern matching
    insights = {
        "writing_style": _analyze_writing_style(content),
        "content_structure": _analyze_content_structure(content),
        "audience_focus": _analyze_audience_focus(content),
        "engagement_techniques": _extract_engagement_techniques(content)
    }
    
    return insights


def _analyze_writing_style(content: str) -> str:
    """Analyze the writing style of Substack content"""
    # Simple heuristic-based analysis
    sentences = re.split(r'[.!?]+', content)
    avg_sentence_length = sum(len(s.split()) for s in sentences if s.strip()) / max(len(sentences), 1)
    
    if avg_sentence_length < 10:
        return "concise"
    elif avg_sentence_length < 20:
        return "balanced"
    else:
        return "detailed"


def _analyze_content_structure(content: str) -> list:
    """Analyze content structure"""
    structure = []
    
    # Look for common structural elements
    if "##" in content or "###" in content:
        structure.append("headings")
    if "```" in content:
        structure.append("code_blocks")
    if "!" in content:
        structure.append("exclamation")
    if "- " in content or "* " in content:
        structure.append("lists")
    if "http" in content:
        structure.append("links")
    
    return structure if structure else ["paragraphs"]


def _analyze_audience_focus(content: str) -> str:
    """Analyze audience focus"""
    content_lower = content.lower()
    
    beginner_keywords = ["beginner", "introduction", "basic", "fundamentals", "getting started"]
    expert_keywords = ["advanced", "expert", "professional", "deep dive", "sophisticated"]
    
    beginner_count = sum(1 for keyword in beginner_keywords if keyword in content_lower)
    expert_count = sum(1 for keyword in expert_keywords if keyword in content_lower)
    
    if beginner_count > expert_count:
        return "beginner_friendly"
    elif expert_count > beginner_count:
        return "expert_level"
    else:
        return "intermediate"


def _extract_engagement_techniques(content: str) -> list:
    """Extract engagement techniques"""
    techniques = []
    
    # Look for common engagement techniques
    if "question" in content.lower() or "?" in content:
        techniques.append("questions")
    if "example" in content.lower() or "e.g." in content.lower():
        techniques.append("examples")
    if "tip" in content.lower() or "hint" in content.lower():
        techniques.append("tips")
    if "note" in content.lower():
        techniques.append("notes")
    
    return techniques


def _extract_engagement_metrics(post: Dict) -> Dict:
    """Extract engagement metrics from Substack post"""
    # This would be enhanced with actual API data when available
    return {
        "likes": post.get("likes", 0),
        "comments": post.get("comments", 0),
        "shares": post.get("shares", 0),
        "estimated_engagement": "medium"  # Default estimate
    }


def _analyze_content_quality(post: Dict) -> Dict:
    """Analyze content quality metrics"""
    return {
        "word_count": len(post.get("description", "").split()),
        "has_images": "img" in post.get("html", ""),
        "has_links": "http" in post.get("description", ""),
        "quality_score": _calculate_content_quality_score(post)
    }


def _calculate_content_quality_score(post: Dict) -> int:
    """Calculate content quality score"""
    # Simple heuristic-based scoring
    score = 50
    
    description = post.get("description", "")
    word_count = len(description.split())
    
    # Word count scoring
    if 200 <= word_count <= 500:
        score += 30
    elif word_count > 500:
        score += 20
    
    # Content richness
    if "img" in post.get("html", ""):
        score += 10
    if "http" in description:
        score += 10
    
    return min(100, max(0, score))


def _enhance_substack_post(post: Dict, query: str) -> Dict:
    """Enhance Substack post with additional analysis"""
    enhanced_post = post.copy()
    
    # Add quality metrics
    enhanced_post["engagement"] = _extract_engagement_metrics(post)
    enhanced_post["content_quality"] = _analyze_content_quality(post)
    enhanced_post["relevance_score"] = _calculate_relevance_score(post, query)
    enhanced_post["type"] = "substack_post"
    
    return enhanced_post


def _calculate_relevance_score(post: Dict, query: str) -> int:
    """Calculate relevance score based on query matching"""
    score = 0
    content = (post.get("title", "") + " " + post.get("description", "")).lower()
    query_lower = query.lower()
    
    # Exact match scoring
    if query_lower in content:
        score += 50
    
    # Word overlap scoring
    query_words = set(query_lower.split())
    content_words = set(content.split())
    overlap = len(query_words & content_words)
    score += min(overlap * 10, 50)
    
    return min(100, max(0, score))