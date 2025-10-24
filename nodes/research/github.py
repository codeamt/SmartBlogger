import requests
from bs4 import BeautifulSoup
import time
# from state import EnhancedBlogState

def execute_github_search(query: str, state: EnhancedBlogState) -> list:
    """Enhanced GitHub repository search with better filtering"""
    try:
        # Use GitHub search API for more reliable results
        headers = {}
        if os.environ.get("GITHUB_TOKEN"):
            headers = {"Authorization": f"token {os.environ.get('GITHUB_TOKEN')}"}

        search_url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc&per_page=5"

        response = requests.get(search_url, headers=headers, timeout=15)
        if response.status_code != 200:
            # Fallback to web scraping
            return github_web_search(query)

        data = response.json()
        results = []

        for repo in data.get('items', [])[:3]:
            # Filter out low-quality repositories
            if should_include_repo(repo):
                results.append({
                    "title": repo['name'],
                    "url": repo['html_url'],
                    "content": repo.get('description', '')[:200],
                    "stars": repo.get('stargazers_count', 0),
                    "language": repo.get('language', ''),
                    "updated": repo.get('updated_at', ''),
                    "topics": repo.get('topics', [])[:5]
                })

        return results

    except Exception as e:
        print(f"GitHub API search error: {e}")
        return github_web_search(query)


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