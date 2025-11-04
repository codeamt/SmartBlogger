from state import EnhancedBlogState
from models.llm_manager import local_llm_manager
from models.summarizer import summarizer
from utils.token_tracking import track_token_usage
import json
import re
import os
import requests


def seo_optimization_node(state: EnhancedBlogState) -> EnhancedBlogState:
    """Optimize blog post for SEO by identifying keywords and providing drafting constraints"""
    try:
        # Generate SEO keywords based on blog structure
        seo_targets = _generate_seo_keywords(state)
        
        # Validate keywords using free SERP API or fallback methods
        validated_keywords = _validate_keywords(seo_targets, state)
        
        # Create SEO drafting constraints
        seo_constraints = _create_seo_constraints(validated_keywords)
        
        # Update state with SEO targets and constraints
        return state.update(
            seo_targets=validated_keywords,
            seo_constraints=seo_constraints,
            next_action="conditional_synthesis"
        )
        
    except Exception as e:
        print(f"SEO optimization failed: {e}")
        return state.update(next_action="conditional_synthesis")


def _generate_seo_keywords(state: EnhancedBlogState) -> dict:
    """Generate primary and secondary keywords using LLM analysis"""
    try:
        researcher_llm = local_llm_manager.get_researcher()
        
        # Get blog structure and content preview
        sections = state.sections or []
        content_summary = state.content_summary or ""
        
        section_titles = [s.get('title', '') for s in sections]
        structure_overview = "\n".join(f"- {title}" for title in section_titles)
        
        prompt = f"""
Analyze this blog post structure and content to generate SEO keywords:

CONTENT SUMMARY:
{content_summary[:1000]}

BLOG STRUCTURE:
{structure_overview}

Generate 5-10 high-value, long-tail keywords for this content.

Return ONLY a JSON object with this structure:
{{
  "primary_keywords": ["main keyword 1", "main keyword 2"],
  "secondary_keywords": ["related keyword 1", "related keyword 2", "related keyword 3"]
}}
"""
        
        response = researcher_llm.invoke([
            ("system", "You are an SEO expert. Generate relevant keywords for technical content. Return ONLY valid JSON."),
            ("human", prompt)
        ])
        
        # Parse response
        content = response.content.strip()
        if content.startswith('{') and content.endswith('}'):
            try:
                keywords = json.loads(content)
                return keywords
            except:
                pass
        
        # Fallback extraction
        json_match = re.search(r'\{[^}]+\}', content)
        if json_match:
            try:
                keywords = json.loads(json_match.group())
                return keywords
            except:
                pass
        
        # Ultimate fallback
        return {
            "primary_keywords": ["technical blog", "programming tutorial"],
            "secondary_keywords": ["code examples", "best practices", "implementation guide"]
        }
        
    except Exception as e:
        print(f"Keyword generation failed: {e}")
        return {
            "primary_keywords": ["technical blog", "programming tutorial"],
            "secondary_keywords": ["code examples", "best practices", "implementation guide"]
        }


def _validate_keywords(seo_targets: dict, state: EnhancedBlogState) -> dict:
    """Validate keywords using SERP API or fallback methods"""
    try:
        # Try to use Google Trends API or SERP API
        primary_keywords = seo_targets.get("primary_keywords", [])
        secondary_keywords = seo_targets.get("secondary_keywords", [])
        
        # Validate using free SERP API (Google Programmable Search or similar)
        validated_primary = []
        validated_secondary = []
        
        # For now, we'll use a simple validation approach
        # In production, this would connect to a SERP API
        for keyword in primary_keywords:
            # Simulate API validation
            validated_primary.append({
                "keyword": keyword,
                "search_volume": _estimate_search_volume(keyword),
                "difficulty": _estimate_difficulty(keyword),
                "competition": "medium"
            })
        
        for keyword in secondary_keywords:
            validated_secondary.append({
                "keyword": keyword,
                "search_volume": _estimate_search_volume(keyword),
                "difficulty": _estimate_difficulty(keyword),
                "competition": "low"
            })
        
        return {
            "primary_keywords": validated_primary,
            "secondary_keywords": validated_secondary
        }
        
    except Exception as e:
        print(f"Keyword validation failed: {e}")
        # Return unvalidated keywords with default metrics
        primary_keywords = seo_targets.get("primary_keywords", [])
        secondary_keywords = seo_targets.get("secondary_keywords", [])
        
        return {
            "primary_keywords": [{"keyword": kw, "search_volume": 1000, "difficulty": "medium", "competition": "medium"} for kw in primary_keywords],
            "secondary_keywords": [{"keyword": kw, "search_volume": 500, "difficulty": "low", "competition": "low"} for kw in secondary_keywords]
        }


def _estimate_search_volume(keyword: str) -> int:
    """Estimate search volume for a keyword (fallback method)"""
    # Simple heuristic-based estimation
    keyword_lower = keyword.lower()
    
    # Base estimates
    if any(word in keyword_lower for word in ["tutorial", "guide", "how to"]):
        return 2500
    elif any(word in keyword_lower for word in ["best", "top", "review"]):
        return 3000
    elif any(word in keyword_lower for word in ["python", "javascript", "react", "api"]):
        return 4000
    else:
        return 1500


def _estimate_difficulty(keyword: str) -> str:
    """Estimate keyword difficulty (fallback method)"""
    keyword_lower = keyword.lower()
    
    # Simple heuristic-based estimation
    if any(word in keyword_lower for word in ["beginner", "basic", "introduction"]):
        return "low"
    elif any(word in keyword_lower for word in ["advanced", "expert", "professional"]):
        return "high"
    else:
        return "medium"


def _create_seo_constraints(validated_keywords: dict) -> dict:
    """Create SEO drafting constraints for the blog post"""
    primary_keywords = validated_keywords.get("primary_keywords", [])
    secondary_keywords = validated_keywords.get("secondary_keywords", [])
    
    # Extract just the keyword strings
    primary_keyword_list = [kw.get("keyword", "") for kw in primary_keywords if kw.get("keyword")]
    secondary_keyword_list = [kw.get("keyword", "") for kw in secondary_keywords if kw.get("keyword")]
    
    return {
        "primary_keywords": primary_keyword_list,
        "secondary_keywords": secondary_keyword_list,
        "target_density": {
            "primary": "1.5-2.5%",
            "secondary": "0.5-1.0%"
        },
        "instructions": f"""
SEO DRAFTING CONSTRAINTS:

Primary Keywords to Target: {', '.join(primary_keyword_list[:3])}
Secondary Keywords to Include: {', '.join(secondary_keyword_list[:5])}

Requirements:
1. Achieve {"1.5-2.5%"} keyword density for primary keywords
2. Naturally integrate secondary keywords throughout the content
3. Use keywords in headings, subheadings, and body text
4. Avoid keyword stuffing - maintain natural, readable prose
5. Include keywords in the first 100 words and last 100 words

The content should read naturally while meeting these SEO targets.
"""
    }


def analyze_keyword_density(content: str, primary_keywords: list, secondary_keywords: list) -> dict:
    """Analyze keyword density in content"""
    if not content:
        return {"primary_density": 0, "secondary_density": 0}
    
    # Simple word count
    words = content.lower().split()
    total_words = len(words)
    
    if total_words == 0:
        return {"primary_density": 0, "secondary_density": 0}
    
    # Count primary keyword occurrences
    primary_count = 0
    for keyword in primary_keywords:
        keyword_words = keyword.lower().split()
        if len(keyword_words) == 1:
            primary_count += words.count(keyword_words[0])
        else:
            # For phrases, count occurrences
            primary_count += content.lower().count(keyword.lower())
    
    # Count secondary keyword occurrences
    secondary_count = 0
    for keyword in secondary_keywords:
        keyword_words = keyword.lower().split()
        if len(keyword_words) == 1:
            secondary_count += words.count(keyword_words[0])
        else:
            secondary_count += content.lower().count(keyword.lower())
    
    primary_density = (primary_count / total_words) * 100 if total_words > 0 else 0
    secondary_density = (secondary_count / total_words) * 100 if total_words > 0 else 0
    
    return {
        "primary_density": round(primary_density, 2),
        "secondary_density": round(secondary_density, 2),
        "primary_count": primary_count,
        "secondary_count": secondary_count,
        "total_words": total_words
    }
