import requests
import zipfile
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Dict
import re

class GitHubDownloader:
    def __init__(self, console=None):
        self.console = console
    
    def parse_github_url(self, url: str) -> Optional[Dict[str, str]]:
        patterns = [
            r'github\.com/([^/]+)/([^/]+)/?$',
            r'github\.com/([^/]+)/([^/]+)\.git/?$',
            r'github\.com/([^/]+)/([^/]+)/tree/([^/]+)/?',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                owner, repo = match.group(1), match.group(2)
                branch = match.group(3) if len(match.groups()) > 2 else 'main'
                return {'owner': owner, 'repo': repo, 'branch': branch}
        
        return None
    
    def download_repo(self, url: str, target_dir: Path) -> bool:
        repo_info = self.parse_github_url(url)
        if not repo_info:
            if self.console:
                self.console.print(f"Invalid GitHub URL: {url}", style="red")
            return False
        
        owner, repo, branch = repo_info['owner'], repo_info['repo'], repo_info['branch']
        download_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip"
        
        if self.console:
            self.console.print(f"Downloading {owner}/{repo} ({branch} branch)...")
        
        try:
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            
            with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp_file:
                for chunk in response.iter_content(chunk_size=8192):
                    tmp_file.write(chunk)
                zip_path = tmp_file.name
            
            target_dir.mkdir(parents=True, exist_ok=True)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(target_dir)
            
            extracted_dirs = list(target_dir.iterdir())
            if len(extracted_dirs) == 1 and extracted_dirs[0].is_dir():
                repo_dir = extracted_dirs[0]
                for item in repo_dir.iterdir():
                    shutil.move(str(item), str(target_dir))
                repo_dir.rmdir()
            
            Path(zip_path).unlink()
            
            if self.console:
                self.console.print(f"Downloaded to {target_dir}", style="green")
            
            return True
            
        except Exception as e:
            if self.console:
                self.console.print(f"Error downloading repo: {e}", style="red")
            return False