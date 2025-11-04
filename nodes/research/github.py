import os
import requests
import re
from bs4 import BeautifulSoup
import time
from state import EnhancedBlogState
from .perplexity import execute_perplexity_search
from .repo_indexer import repo_indexer_node

def execute_github_search(query: str, state: EnhancedBlogState) -> list:
    """Enhanced GitHub search that can index repositories when needed"""
    try:
        # First try Perplexity search for general results
        site_query = f"site:github.com {query}"
        results = execute_perplexity_search(site_query, state)
        
        # Check if we should index any repositories from the results
        repo_urls = _extract_repo_urls_from_results(results)
        if repo_urls:
            # Index repositories and add to research context
            _index_repositories(repo_urls, state)
        
        return results
    except Exception as e:
        print(f"GitHub search error: {e}")
        return []


def github_web_search(query: str) -> list:
    """Fallback GitHub web search with repository indexing capability"""
    try:
        url = f"https://github.com/search?q={query}&type=repositories"
        response = requests.get(url, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")

        results = []
        repo_urls = []
        
        for repo in soup.select(".repo-list-item")[:3]:
            title_elem = repo.select_one(".v-align-middle")
            desc_elem = repo.select_one(".mb-1")

            if title_elem:
                repo_url = "https://github.com" + title_elem["href"]
                results.append({
                    "title": title_elem.text.strip(),
                    "url": repo_url,
                    "content": desc_elem.text.strip()[:200] if desc_elem else "",
                    "stars": "N/A",  # Not easily available in web version
                    "language": "N/A",
                    "updated": "N/A"
                })
                repo_urls.append(repo_url)
        
        # Index repositories if we found any
        if repo_urls:
            # This would normally index repositories, but we'll skip for now
            # to avoid making this function too complex
            pass

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


def _extract_repo_urls_from_results(results: list) -> list:
    """Extract GitHub repository URLs from search results"""
    repo_urls = []
    
    for result in results:
        url = result.get('url', '')
        if url and 'github.com' in url:
            # Check if it's a repository URL (not an issue, wiki, etc.)
            # Simple pattern: github.com/owner/repo (with optional path)
            import re
            repo_pattern = r'https://github\.com/[^/]+/[^/]+/?'
            match = re.search(repo_pattern, url)
            if match:
                repo_urls.append(match.group(0))
    
    # Remove duplicates
    return list(set(repo_urls))


def _index_repositories(repo_urls: list, state: EnhancedBlogState) -> None:
    """Index repositories and add them to the research context"""
    # This is a simplified version - in a full implementation,
    # this would use the repo_indexer_node to actually index repositories
    # For now, we'll just note that indexing is available
    
    research_context = state.research_context or {}
    if "github_repos_to_index" not in research_context:
        research_context["github_repos_to_index"] = []
    
    # Add unique URLs
    existing_urls = set(research_context["github_repos_to_index"])
    for url in repo_urls:
        if url not in existing_urls:
            research_context["github_repos_to_index"].append(url)
    
    # Update state (this would normally be done in a separate node)
    # For now, we'll just leave it as a marker that indexing is available