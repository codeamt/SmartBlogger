import asyncio
from typing import Dict, Any
from state import EnhancedBlogState
from services.github_repo_service import RepoToTextService


class RepoIndexerNode:
    def __init__(self, github_token: str = None):
        self.github_token = github_token
        self.service = RepoToTextService(github_token)
    
    async def run(self, state: EnhancedBlogState) -> Dict[str, Any]:
        """Index GitHub repositories and convert them to text format for research"""
        try:
            # Get repository URLs from research context or state
            repo_urls = self._extract_repo_urls(state)
            
            if not repo_urls:
                return {"repo_texts": [], "next_action": "conduct_research"}
            
            # Process each repository
            repo_texts = []
            for repo_url in repo_urls[:3]:  # Limit to first 3 repos to avoid overload
                try:
                    repo_text = await self._index_repository(repo_url)
                    repo_texts.append({
                        "url": repo_url,
                        "content": repo_text,
                        "size": len(repo_text)
                    })
                except Exception as e:
                    print(f"Failed to index repository {repo_url}: {e}")
                    continue
            
            return {
                "repo_texts": repo_texts,
                "next_action": "conduct_research"
            }
            
        except Exception as e:
            print(f"Repo indexing failed: {e}")
            return {"repo_texts": [], "next_action": "conduct_research"}
    
    def _extract_repo_urls(self, state: EnhancedBlogState) -> list:
        """Extract repository URLs from research context or queries"""
        repo_urls = []
        
        # Check research context for GitHub URLs
        if state.research_context:
            for source, results in state.research_context.get("by_source", {}).items():
                if source == "github" and results:
                    for result in results:
                        url = result.get("url", "")
                        if url and "github.com" in url:
                            repo_urls.append(url)
        
        # Check research queries for GitHub references
        if state.research_queries:
            for query in state.research_queries:
                # Simple pattern matching for GitHub URLs in queries
                if "github.com/" in query:
                    # Extract URL from query
                    import re
                    urls = re.findall(r'https://github\.com/[\w.-]+/[\w.-]+', query)
                    repo_urls.extend(urls)
        
        # Remove duplicates
        return list(set(repo_urls))
    
    async def _index_repository(self, repo_url: str) -> str:
        """Index a single repository and convert it to text"""
        # Parse repository URL
        meta = self.service.parse_repo_url(repo_url)
        
        # Get repository SHA
        sha = await self.service.fetch_repo_sha(meta["owner"], meta["repo"])
        
        # Get repository tree
        tree = await self.service.fetch_repo_tree(meta["owner"], meta["repo"], sha)
        
        # Filter files to include
        files = [f for f in tree if f["type"] == "blob" and self.service.should_include_file(f["path"])]
        
        # Limit number of files to avoid overload
        files = files[:50]  # Process at most 50 files
        
        # Fetch file contents
        file_contents = await self.service.fetch_file_contents(files)
        
        # Format as text
        return self.service.format_repo_contents(file_contents)


def repo_indexer_node(state: EnhancedBlogState) -> EnhancedBlogState:
    """Synchronous wrapper for the repo indexer node"""
    try:
        # Get GitHub token from environment
        import os
        github_token = os.getenv("GITHUB_TOKEN")
        
        # Create and run the async node
        node = RepoIndexerNode(github_token)
        result = asyncio.run(node.run(state))
        
        # Update state with repo texts
        repo_texts = result.get("repo_texts", [])
        
        # Add repo texts to research context
        research_context = state.research_context or {}
        if "github_repos" not in research_context:
            research_context["github_repos"] = []
        
        research_context["github_repos"].extend(repo_texts)
        
        return state.update(
            research_context=research_context,
            next_action=result.get("next_action", "conduct_research")
        )
        
    except Exception as e:
        print(f"Repo indexing node failed: {e}")
        return state.update(next_action="conduct_research")
