"""
GitHub repository management
"""

import os
import subprocess
import logging
import tempfile
import shutil
from github import Github, GithubException
import time
import requests

logger = logging.getLogger(__name__)

class GitHubManager:
    def __init__(self, config):
        self.config = config
        self.github = Github(config.GITHUB_TOKEN)
        self.user = self.github.get_user()

    def create_and_push_repo(self, repo_name, app_code, task_brief):
        try:
            temp_dir = tempfile.mkdtemp()
            logger.info(f"Created temp directory: {temp_dir}")

            try:
                repo = self._create_github_repo(repo_name, task_brief)
                self._init_local_repo(temp_dir)
                self._write_app_files(temp_dir, app_code)
                self._add_license(temp_dir)
                self._create_readme(temp_dir, repo_name, task_brief, app_code)
                commit_sha = self._commit_and_push(temp_dir, repo)
                pages_url = self._enable_github_pages(repo)
                self._wait_for_pages(pages_url)

                logger.info(f"Successfully completed! Repo: {repo.html_url}")
                return repo.html_url, commit_sha, pages_url
            finally:
                shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception as e:
            logger.error(f"Error: {str(e)}", exc_info=True)
            raise

    def _create_github_repo(self, repo_name, description):
        try:
            try:
                existing_repo = self.user.get_repo(repo_name)
                logger.warning(f"Repo {repo_name} already exists, deleting...")
                existing_repo.delete()
                time.sleep(2)
            except GithubException:
                pass

            repo = self.user.create_repo(
                name=repo_name,
                description=description[:100] if description else "LLM-generated app",
                private=False,
                auto_init=False
            )
            logger.info(f"Created repo: {repo.html_url}")
            return repo
        except GithubException as e:
            logger.error(f"GitHub API error: {str(e)}")
            raise

    def _init_local_repo(self, repo_dir):
        subprocess.run(['git', 'init'], cwd=repo_dir, check=True, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', self.config.GITHUB_USERNAME], 
                      cwd=repo_dir, check=True, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 
                       f'{self.config.GITHUB_USERNAME}@users.noreply.github.com'], 
                      cwd=repo_dir, check=True, capture_output=True)
        subprocess.run(['git', 'checkout', '-b', self.config.DEFAULT_BRANCH], 
                      cwd=repo_dir, check=True, capture_output=True)

    def _write_app_files(self, repo_dir, app_code):
        for filename, content in app_code.items():
            filepath = os.path.join(repo_dir, filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Wrote file: {filename}")

    def _add_license(self, repo_dir):
        mit = f"""MIT License

Copyright (c) {time.strftime("%Y")} {self.config.GITHUB_USERNAME}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
        with open(os.path.join(repo_dir, 'LICENSE'), 'w') as f:
            f.write(mit)
        logger.info("Added MIT LICENSE")

    def _create_readme(self, repo_dir, repo_name, task_brief, app_code):
        readme = f"""# {repo_name}

## Summary
LLM-generated web application.

**Brief:** {task_brief}

**Live Demo:** https://{self.config.GITHUB_USERNAME}.github.io/{repo_name}/

## Setup
This is a static web app. To run locally:

```bash
# Clone the repository
git clone https://github.com/{self.config.GITHUB_USERNAME}/{repo_name}.git
cd {repo_name}

# Open in browser
open index.html

# Or use a local server
python -m http.server 8000
```

## Files
"""
        for filename in sorted(app_code.keys()):
            readme += f"- `{filename}`: Application file\n"

        readme += f"""
## Usage
Open `index.html` in your web browser.

## License
MIT License - See LICENSE file for details.

## Generated
Generated on {time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())} using LLM technology.
"""

        with open(os.path.join(repo_dir, 'README.md'), 'w') as f:
            f.write(readme)
        logger.info("Created README.md")

    def _commit_and_push(self, repo_dir, repo):
        subprocess.run(['git', 'add', '.'], cwd=repo_dir, check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Initial commit: LLM-generated application'], 
                      cwd=repo_dir, check=True, capture_output=True)

        result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                              cwd=repo_dir, check=True, capture_output=True, text=True)
        commit_sha = result.stdout.strip()

        remote_url = f"https://{self.config.GITHUB_TOKEN}@github.com/{self.config.GITHUB_USERNAME}/{repo.name}.git"
        subprocess.run(['git', 'remote', 'add', 'origin', remote_url], 
                      cwd=repo_dir, check=True, capture_output=True)
        subprocess.run(['git', 'push', '-u', 'origin', self.config.DEFAULT_BRANCH], 
                      cwd=repo_dir, check=True, capture_output=True)

        logger.info(f"Pushed commit: {commit_sha}")
        return commit_sha

    def _enable_github_pages(self, repo):
        """Enable GitHub Pages using REST API directly"""
        try:
            pages_url = f"https://{self.config.GITHUB_USERNAME}.github.io/{repo.name}/"

            # Method 1: Try using PyGithub's internal API
            try:
                logger.info("Attempting to enable GitHub Pages...")

                # Use the REST API directly
                api_url = f"https://api.github.com/repos/{self.config.GITHUB_USERNAME}/{repo.name}/pages"
                headers = {
                    'Authorization': f'token {self.config.GITHUB_TOKEN}',
                    'Accept': 'application/vnd.github.v3+json'
                }
                data = {
                    'source': {
                        'branch': self.config.DEFAULT_BRANCH,
                        'path': '/'
                    }
                }

                response = requests.post(api_url, json=data, headers=headers)

                if response.status_code in [201, 409]:  # 201 = created, 409 = already exists
                    if response.status_code == 201:
                        logger.info("GitHub Pages enabled successfully!")
                    else:
                        logger.info("GitHub Pages already enabled")
                    return pages_url
                else:
                    logger.warning(f"Pages API returned {response.status_code}: {response.text}")

            except Exception as e:
                logger.warning(f"Could not enable Pages via API: {str(e)}")

            # Method 2: Enable via repository settings update
            try:
                logger.info("Trying alternative method...")
                repo.edit(has_pages=True)
                time.sleep(2)
                logger.info("GitHub Pages should be enabled")
            except Exception as e:
                logger.warning(f"Alternative method failed: {str(e)}")

            # Return the expected Pages URL regardless
            logger.info(f"Pages URL will be: {pages_url}")
            logger.info("Note: You may need to enable Pages manually in repo settings")
            return pages_url

        except Exception as e:
            logger.error(f"Error enabling GitHub Pages: {str(e)}")
            # Return the expected URL anyway
            pages_url = f"https://{self.config.GITHUB_USERNAME}.github.io/{repo.name}/"
            logger.info(f"Expected Pages URL: {pages_url}")
            return pages_url

    def _wait_for_pages(self, pages_url, max_wait=120):
        """Wait for GitHub Pages to become available"""
        logger.info("Waiting for GitHub Pages to be ready...")
        logger.info("Note: GitHub Pages can take 2-5 minutes to build")

        start_time = time.time()

        while time.time() - start_time < max_wait:
            try:
                response = requests.get(pages_url, timeout=10)
                if response.status_code == 200:
                    logger.info(f"✅ GitHub Pages is live at: {pages_url}")
                    return True
            except Exception:
                pass

            elapsed = int(time.time() - start_time)
            if elapsed % 15 == 0 and elapsed > 0:
                logger.info(f"Still waiting... ({elapsed}s elapsed)")

            time.sleep(5)

        logger.warning(f"GitHub Pages not ready after {max_wait}s")
        logger.info("This is normal - Pages can take a few minutes to build")
        logger.info(f"Check manually at: {pages_url}")
        return False
