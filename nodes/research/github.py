import os
import requests
from bs4 import BeautifulSoup
import time
from state import EnhancedBlogState
from .perplexity import execute_perplexity_search

def execute_github_search(query: str, state: EnhancedBlogState) -> list:
    """Proxy GitHub search via Perplexity using a site filter."""
    try:
        site_query = f"site:github.com {query}"
        return execute_perplexity_search(site_query, state)
    except Exception as e:
        print(f"GitHub search (Perplexity) error: {e}")
        return []


def github_web_search(query: str) -> list:
    """Fallback GitHub web search"""
    try:
        url = f"https://github.com/search?q={query}&type=repositories"
        response = requests.get(url, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")

        results = []
        for repo in soup.select(".repo-list-item")[:3]:
            title_elem = repo.select_one(".v-align-middle")
            desc_elem = repo.select_one(".mb-1")

            if title_elem:
                results.append({
                    "title": title_elem.text.strip(),
                    "url": "https://github.com" + title_elem["href"],
                    "content": desc_elem.text.strip()[:200] if desc_elem else "",
                    "stars": "N/A",  # Not easily available in web version
                    "language": "N/A",
                    "updated": "N/A"
                })

        return results
    except Exception as e:
        print(f"GitHub web search error: {e}")
        return []


def should_include_repo(repo: dict) -> bool:
    """Filter repositories by quality metrics"""
    # Exclude archived repositories
    if repo.get('archived'):
        return False

    # Exclude forks unless they have significant stars
    if repo.get('fork') and repo.get('stargazers_count', 0) < 100:
        return False

    # Prefer repositories with descriptions
    if not repo.get('description'):
        return False

    # Minimum star threshold for quality
    if repo.get('stargazers_count', 0) < 10:
        return False

    return True