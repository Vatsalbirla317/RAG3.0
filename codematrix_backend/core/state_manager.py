import asyncio
import os
import json
from typing import Optional

# A simple in-memory dictionary to hold the application's state.
# In a real production app, you might use Redis or another proper state store.
app_state = {
    "status": "idle",
    "message": "Awaiting repository.",
    "progress": 0.0,
    "repo_path": None,
    "repo_name": None,
    "repo_description": "No repository loaded.",
    "repo_metadata": {},
    "is_processing": False,  # <-- ADD THIS LINE
    "last_updated": None
}

# A lock to prevent race conditions when updating the state from different requests.
state_lock = asyncio.Lock()

# File path for persistent state storage
STATE_FILE = "/tmp/codematrix_state.json"

def _get_repo_name_from_path(repo_path: Optional[str]) -> Optional[str]:
    """Extract repository name from path if available"""
    if repo_path and os.path.exists(repo_path):
        return os.path.basename(repo_path)
    return None

def _load_persistent_state():
    """Load state from persistent storage if available"""
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r') as f:
                saved_state = json.load(f)
                app_state.update(saved_state)
                print(f"✅ Loaded persistent state: {saved_state.get('repo_name', 'None')}")
                return True
    except Exception as e:
        print(f"⚠️ Could not load persistent state: {e}")
    return False

def _save_persistent_state():
    """Save current state to persistent storage"""
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(app_state, f)
    except Exception as e:
        print(f"⚠️ Could not save persistent state: {e}")

async def update_state(status=None, message=None, progress=None, repo_path=None, repo_name=None, repo_metadata=None, is_processing=None):
    async with state_lock:
        if status is not None:
            app_state["status"] = status
        if message is not None:
            app_state["message"] = message
        if progress is not None:
            app_state["progress"] = progress
        if repo_path is not None:
            app_state["repo_path"] = repo_path
            # Auto-extract repo_name from path if not provided
            if repo_name is None:
                repo_name = _get_repo_name_from_path(repo_path)
        if repo_name is not None:
            app_state["repo_name"] = repo_name
        if repo_metadata is not None:
            app_state["repo_metadata"] = repo_metadata
        if is_processing is not None:
            app_state["is_processing"] = is_processing
        
        # Update timestamp
        import datetime
        app_state["last_updated"] = datetime.datetime.now().isoformat()
        
        # Save to persistent storage
        _save_persistent_state()
        
        print(f"State updated: {app_state}")

async def get_state():
    async with state_lock:
        return app_state.copy()

async def reset_state():
    """Reset state to initial values"""
    async with state_lock:
        app_state.update({
            "status": "idle",
            "message": "Awaiting repository.",
            "progress": 0.0,
            "repo_path": None,
            "repo_name": None,
            "repo_description": "No repository loaded.",
            "repo_metadata": {},
            "is_processing": False,
            "last_updated": None
        })
        # Clear persistent storage
        try:
            if os.path.exists(STATE_FILE):
                os.remove(STATE_FILE)
        except Exception as e:
            print(f"⚠️ Could not remove persistent state: {e}")
        print("State reset to initial values")

# Load persistent state on module import
_load_persistent_state() 