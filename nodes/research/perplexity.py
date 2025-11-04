import requests
import os
import re
import hashlib
from typing import List, Dict, Any


def execute_perplexity_search(query: str, state=None) -> list:
    """Use Perplexity API for high-quality web search with enhanced validation and filtering"""
    api_key = os.environ.get("PERPLEXITY_API_KEY")
    if not api_key:
        # Update state if provided
        if state:
            state.research_status = "Perplexity_Failed"
        return []

    try:
        url = "https://api.perplexity.ai/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # Build model try-order: env first, then known-good fallbacks
        last_error = None
        env_model = os.getenv("PERPLEXITY_MODEL", "sonar")
        try_order = [env_model] if env_model else []
        # Append common online models (avoid duplicates / Nones)
        for m in ["sonar", "sonar-medium-online", "sonar-small-online"]:
            if m and m not in try_order:
                try_order.append(m)

        last_error = None
        for model_name in try_order:
            payload = {
                "model": model_name,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a research assistant. Provide accurate, recent information with sources. Focus on technical and programming topics."
                    },
                    {
                        "role": "user",
                        "content": _generate_perplexity_prompt(query)
                    }
                ],
                "max_tokens": 1000
            }

            response = requests.post(url, json=payload, headers=headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
                results = parse_perplexity_response(content, query)
                
                # Apply deduplication and filtering
                filtered_results = filter_and_deduplicate_results(results, query)
                
                # Enrich with metadata
                enriched_results = enrich_results_with_metadata(filtered_results, query)
                
                return enriched_results
            else:
                text = response.text[:160].replace("\n", " ") if hasattr(response, 'text') else ""
                print(f"Perplexity API error for model '{model_name}': {response.status_code} {text}")
                last_error = (response.status_code, text)

        # If all models failed
        if state:
            state.research_status = "Perplexity_Failed"
        return []

    except Exception as e:
        print(f"Perplexity search error: {e}")
        if state:
            state.research_status = "Perplexity_Failed"
        return []


def parse_perplexity_response(content: str, query: str) -> list:
    """Parse Perplexity API response into structured results with validation"""
    # Handle empty or invalid content
    if not content or not isinstance(content, str):
        print(f"Perplexity returned empty or invalid content for query: {query}")
        return []
    
    # Check if this is a competitor search query
    is_competitor_search = any(keyword in query.lower() for keyword in ["best performing", "high traffic", "popular blog", "top articles", "successful posts"])
    
    if is_competitor_search:
        return _parse_competitor_search_response(content, query)
    
    lines = [l.strip() for l in content.split('\n') if l.strip()]
    results = []
    current = None

    bullet_re = re.compile(r"^(?:[•\-\*]|\d+\.)\s*(.+)$")

    for line in lines:
        m = bullet_re.match(line)
        if m:
            # Start a new item
            if current and current.get('content'):
                results.append(current)
            text = m.group(1).strip()
            current = {
                'content': text,
                'title': ' '.join(text.split()[:8]) or query
            }
            continue

        if line.startswith('http'):
            if not current:
                current = {'content': query, 'title': query}
            current['url'] = line
            if 'title' not in current or not current['title']:
                current['title'] = query

    if current and current.get('content'):
        results.append(current)

    # If nothing matched bullets, try to split paragraphs
    if not results:
        para = content.split('\n\n')
        for p in para:
            text = p.strip()
            if len(text) > 20:
                results.append({'content': text, 'title': ' '.join(text.split()[:8])})
                if len(results) >= 5:
                    break
    
    # Validate results format
    validated_results = []
    for result in results:
        if isinstance(result, dict) and result.get('content'):
            validated_results.append(result)
        else:
            print(f"Skipping invalid result format: {result}")
    
    return validated_results[:5]


def filter_and_deduplicate_results(results: List[Dict], query: str) -> List[Dict]:
    """Filter out low-quality results and remove duplicates"""
    if not results:
        return []
    
    # Filter out too short results
    filtered_results = []
    for result in results:
        content = result.get('content', '')
        if len(content.split()) >= 10:  # At least 10 words
            filtered_results.append(result)
    
    # Remove duplicates based on content similarity
    unique_results = []
    seen_hashes = set()
    
    for result in filtered_results:
        content = result.get('content', '')
        # Create a hash of the content for duplicate detection
        content_hash = hashlib.md5(content.encode()).hexdigest()
        
        if content_hash not in seen_hashes:
            seen_hashes.add(content_hash)
            unique_results.append(result)
    
    return unique_results


def enrich_results_with_metadata(results: List[Dict], query: str) -> List[Dict]:
    """Enrich results with metadata including the original query"""
    enriched_results = []
    
    for result in results:
        enriched_result = result.copy()
        # Add the original query that generated this result
        enriched_result['original_query'] = query
        # Add a timestamp
        import time
        enriched_result['retrieved_at'] = time.time()
        # Add a source identifier
        enriched_result['source'] = 'perplexity'
        enriched_results.append(enriched_result)
    
    return enriched_results


def _generate_perplexity_prompt(query: str) -> str:
    """Generate appropriate prompt based on query type"""
    query_lower = query.lower()
    
    # Check if this is a competitor search query
    if any(keyword in query_lower for keyword in ["best performing", "high traffic", "popular blog", "top articles", "successful posts"]):
        return f"""Find high-authority blog posts and articles about: {query}

Focus on these high-authority sources: Medium, Forbes, dedicated industry blogs, official documentation sites.

For each result, provide:
1. The article title
2. The main H2 and H3 headings (structural outline)
3. A brief analysis of the tone/style (e.g., "Very academic, uses numbered lists, focuses on real-world case studies")
4. The URL

Include 3-5 key findings with sources from the last 2 years."""
    else:
        # Standard research query
        return f"Search for: {query}. Provide 3-5 key findings with sources from the last 2 years. Include URLs."


def _parse_competitor_search_response(content: str, query: str) -> list:
    """Parse competitor search response to extract structural outlines and tone analysis"""
    if not content or not isinstance(content, str):
        return []
    
    # Split content into sections (assuming each competitor article is a separate section)
    sections = content.split('\n\n')
    results = []
    
    for section in sections:
        if not section.strip():
            continue
        
        lines = [line.strip() for line in section.split('\n') if line.strip()]
        if not lines:
            continue
        
        # Extract title (first line or line with URL)
        title = ""
        url = ""
        outline = []
        tone_analysis = ""
        
        # Look for URL first
        for i, line in enumerate(lines):
            if line.startswith('http'):
                url = line
                # Title is usually the line before URL
                if i > 0:
                    title = lines[i-1]
                break
        
        # If no URL found, use first line as title
        if not title and lines:
            title = lines[0]
        
        # Extract structural outline (H2/H3 headings)
        for line in lines:
            if any(marker in line for marker in ['##', '###', '**', '__']):
                # This looks like a heading
                clean_line = re.sub(r'[#*_]+', '', line).strip()
                if clean_line and len(clean_line) > 10:  # Only substantial headings
                    outline.append(clean_line)
        
        # Extract tone analysis (look for descriptive phrases)
        tone_indicators = ["academic", "casual", "formal", "technical", "beginner", "advanced", 
                          "list", "step", "case study", "example", "practical", "theoretical"]
        
        for line in lines:
            line_lower = line.lower()
            if any(indicator in line_lower for indicator in tone_indicators):
                tone_analysis = line
                break
        
        # Create structured result
        if title or url:
            result = {
                'title': title or "Competitor Article",
                'url': url,
                'content': section[:500] + "..." if len(section) > 500 else section,
                'competitor_outline': outline[:10],  # Limit to 10 headings
                'tone_analysis': tone_analysis or "Not specified",
                'type': 'competitor_analysis'
            }
            results.append(result)
    
    return results[:5]  # Limit to 5 competitor analyses