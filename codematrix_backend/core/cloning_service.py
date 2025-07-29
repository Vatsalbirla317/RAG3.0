import git
import os
from urllib.parse import urlparse
from .state_manager import update_state

REPO_DIR = "repositories"

async def clone_and_process_repo(repo_url: str):
    try:
        repo_name = os.path.basename(urlparse(repo_url).path).replace('.git', '')
        repo_path = os.path.join(REPO_DIR, repo_name)

        await update_state(status="cloning", message=f"Cloning {repo_name}...", progress=0.1, repo_name=repo_name)

        if os.path.exists(repo_path):
            print(f"Repository {repo_name} already exists. Pulling latest changes.")
            repo = git.Repo(repo_path)
            origin = repo.remotes.origin
            origin.pull()
        else:
            print(f"Cloning new repository: {repo_url}")
            os.makedirs(REPO_DIR, exist_ok=True)
            git.Repo.clone_from(repo_url, repo_path, progress=None) # Progress handled by state updates

        await update_state(
            status="ready",  # For now, we'll skip indexing and go straight to 'ready'
            message="Repository successfully cloned.",
            progress=1.0,
            repo_path=repo_path,
        )
        print(f"Successfully processed {repo_name}")

    except Exception as e:
        print(f"Error cloning repository: {e}")
        await update_state(status="error", message=str(e), progress=0.0) 