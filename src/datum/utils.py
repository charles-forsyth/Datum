import hashlib
import os
import subprocess
from typing import Optional


def get_git_provenance() -> dict[str, str]:
    """Gets the Git remote URL and commit hash of the current repository."""
    try:
        # Get the remote URL
        url_result = subprocess.run(
            ['git', 'config', '--get', 'remote.origin.url'],
            capture_output=True, text=True, check=True
        )
        url = url_result.stdout.strip()

        # Get the current commit hash
        hash_result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            capture_output=True, text=True, check=True
        )
        commit_hash = hash_result.stdout.strip()

        return {'repo_url': url, 'commit_hash': commit_hash}
    except (subprocess.CalledProcessError, FileNotFoundError):
        return {'repo_url': 'N/A', 'commit_hash': 'N/A'}

def hash_file(filename: str) -> Optional[str]:
    """Calculates the SHA-256 hash of a file."""
    if not os.path.exists(filename):
        return None
    hasher = hashlib.sha256()
    try:
        with open(filename, 'rb') as f:
            chunk = f.read(4096)
            while chunk:
                hasher.update(chunk)
                chunk = f.read(4096)
        return hasher.hexdigest()
    except Exception:
        return None
