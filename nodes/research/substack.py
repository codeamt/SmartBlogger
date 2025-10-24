import os
import requests


def execute_substack_search(query: str, state=None) -> list:
    """Enhanced Substack search with API if available"""
    try:
        # Try Substack API first
        api_key = os.environ.get("SUBSTACK_API_KEY")
        if api_key:
            return substack_api_search(query, api_key)
        else:
            return substack_web_search(query)
    except Exception as e:
        print(f"Substack search error: {e}")
        return []


def substack_api_search(query: str, api_key: str) -> list:
    """Search Substack using official API"""
    headers = {"Authorization": f"Bearer {api_key}"}
    search_url = f"https://api.substack.com/v1/search/posts?query={query}&limit=3"

    response = requests.get(search_url, headers=headers, timeout=15)
    if response.status_code == 200:
        data = response.json()
        results = []

        for post in data.get('posts', [])[:3]:
            results.append({
                "title": post.get('title', ''),
                "url": post.get('canonical_url', ''),
                "content": post.get('description', '')[:200] + "...",
                "author": post.get('author', {}).get('name', ''),
                "published": post.get('post_date', ''),
                "subscriber_count": post.get('subscriber_count', 0)
            })

        return results
    return []


def substack_web_search(query: str) -> list:
    """Fallback web search for Substack"""
    try:
        # This is a simplified version - Substack's actual search is complex
        # Consider using a search API that indexes Substack
        search_url = f"https://substack.com/api/v1/search/posts?query={query}"
        response = requests.get(search_url, timeout=15)

        if response.status_code == 200:
            data = response.json()
            results = []

            for post in data.get('posts', [])[:3]:
                results.append({
                    "title": post.get('title', ''),
                    "url": post.get('canonical_url', ''),
                    "content": post.get('description', '')[:200] + "...",
                    "author": post.get('author', {}).get('name', ''),
                    "published": post.get('post_date', '')
                })

            return results
    except:
        pass

    return []  # Return empty if no Substack access