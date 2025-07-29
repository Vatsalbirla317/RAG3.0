import asyncio

# A simple in-memory dictionary to hold the application's state.
# In a real production app, you might use Redis or another proper state store.
app_state = {
    "status": "idle",
    "message": "Awaiting repository.",
    "progress": 0.0,
    "repo_path": None,
    "repo_name": None,
    "repo_description": "No repository loaded."
}

# A lock to prevent race conditions when updating the state from different requests.
state_lock = asyncio.Lock()

async def update_state(status=None, message=None, progress=None, repo_path=None, repo_name=None):
    async with state_lock:
        if status is not None:
            app_state["status"] = status
        if message is not None:
            app_state["message"] = message
        if progress is not None:
            app_state["progress"] = progress
        if repo_path is not None:
            app_state["repo_path"] = repo_path
        if repo_name is not None:
            app_state["repo_name"] = repo_name

async def get_state():
    async with state_lock:
        return app_state.copy() 