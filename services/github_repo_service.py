import httpx
import re
from typing import List, Dict, Optional
from zipfile import ZipFile
from io import BytesIO

GITHUB_API = "https://api.github.com"


class RepoToTextService:
    def __init__(self, access_token: Optional[str] = None):
        self.headers = {"Accept": "application/vnd.github+json"}
        if access_token:
            self.headers["Authorization"] = f"token {access_token}"

    async def _fetch_json(self, url: str) -> dict:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.get(url, headers=self.headers)
            if r.status_code == 403 and r.headers.get("X-RateLimit-Remaining") == "0":
                raise RuntimeError("GitHub API rate limit exceeded.")
            if r.status_code == 404:
                raise RuntimeError("Repository, branch, or path not found.")
            r.raise_for_status()
            return r.json()

    @staticmethod
    def parse_repo_url(url: str) -> dict:
        url = url.rstrip("/")
        pattern = r"^https://github\.com/([^/]+)/([^/]+)(/tree/(.+))?$"
        m = re.match(pattern, url)
        if not m:
            raise ValueError("Invalid GitHub repository URL.")
        return {
            "owner": m.group(1),
            "repo": m.group(2),
            "last_string": m.group(4) or ""
        }

    async def get_references(self, owner: str, repo: str) -> dict:
        async with httpx.AsyncClient(timeout=30) as client:
            branches = await client.get(f"{GITHUB_API}/repos/{owner}/{repo}/git/matching-refs/heads/", headers=self.headers)
            tags = await client.get(f"{GITHUB_API}/repos/{owner}/{repo}/git/matching-refs/tags/", headers=self.headers)
            if not branches.is_success or not tags.is_success:
                raise RuntimeError("Failed to fetch references.")
            bjson, tjson = branches.json(), tags.json()
            return {
                "branches": [b["ref"].split("/")[2] for b in bjson],
                "tags": [t["ref"].split("/")[2] for t in tjson],
            }

    async def fetch_repo_sha(self, owner: str, repo: str, ref: str = "", path: str = "") -> str:
        url = f"{GITHUB_API}/repos/{owner}/{repo}/contents/{path}"
        if ref:
            url += f"?ref={ref}"
        data = await self._fetch_json(url)
        return data["sha"]

    async def fetch_repo_tree(self, owner: str, repo: str, sha: str) -> List[dict]:
        url = f"{GITHUB_API}/repos/{owner}/{repo}/git/trees/{sha}?recursive=1"
        data = await self._fetch_json(url)
        return data.get("tree", [])

    async def fetch_file_contents(self, files: List[dict]) -> List[dict]:
        results = []
        async with httpx.AsyncClient(timeout=30) as client:
            for f in files:
                r = await client.get(f["url"], headers={"Accept": "application/vnd.github.v3.raw", **self.headers})
                if not r.is_success:
                    raise RuntimeError(f"Failed to fetch {f['path']}: {r.text}")
                results.append({"path": f["path"], "text": r.text})
        return results

    def format_repo_contents(self, file_contents: List[dict]) -> str:
        formatted = []
        for f in file_contents:
            # Skip binary files and very large files
            if self._is_binary_file(f["text"]):
                formatted.append(f"\n## {f['path']}\n[BINARY FILE - SKIPPED]\n")
            elif len(f["text"]) > 100000:  # Skip files larger than 100KB
                formatted.append(f"\n## {f['path']}\n[LARGE FILE - SKIPPED]\n")
            else:
                formatted.append(f"\n## {f['path']}\n{f['text']}\n")
        return "\n".join(formatted)

    def _is_binary_file(self, content: str) -> bool:
        """Simple heuristic to detect binary files"""
        try:
            content.encode('utf-8')
        except UnicodeError:
            return True
        
        # Check for null bytes which are common in binary files
        if '\x00' in content:
            return True
            
        return False

    def create_zip(self, file_contents: List[dict]) -> bytes:
        buf = BytesIO()
        with ZipFile(buf, "w") as zf:
            for f in file_contents:
                safe_path = f["path"].lstrip("/")
                zf.writestr(safe_path, f["text"])
        buf.seek(0)
        return buf.read()

    def should_include_file(self, file_path: str) -> bool:
        """Determine if a file should be included in the text representation"""
        # Skip common binary file extensions
        binary_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.pdf', '.zip', '.tar', '.gz',
                           '.exe', '.dll', '.so', '.dylib', '.class', '.o', '.obj', '.bin', '.dat'}
        
        # Skip common build/dependency directories
        skip_paths = {'node_modules/', 'venv/', '__pycache__/', '.git/', '.vscode/', '.idea/',
                     'build/', 'dist/', 'target/', '.gradle/', '.mvn/'}
        
        # Check file extension
        if any(file_path.lower().endswith(ext) for ext in binary_extensions):
            return False
            
        # Check path prefixes
        if any(file_path.startswith(path) for path in skip_paths):
            return False
            
        return True
