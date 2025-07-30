# core/cloning_service.py
import os
import git
import shutil
import time
from urllib.parse import urlparse

from langchain.text_splitter import Language, RecursiveCharacterTextSplitter
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain_community.vectorstores import Chroma

from .state_manager import update_state
from .ai_service import gemini_embeddings

REPO_DIR = "repositories"
VECTOR_DB_DIR = "vector_db"

async def clone_and_process_repo(repo_url: str):
    try:
        # SET THE LOCK
        await update_state(is_processing=True)
        
        repo_name = os.path.basename(urlparse(repo_url).path).replace('.git', '')
        repo_path = os.path.join(REPO_DIR, repo_name)
        vector_db_path = os.path.join(VECTOR_DB_DIR, repo_name)

        # --- 1. SMART CLONING / PULLING ---
        await update_state(status="cloning", message=f"Accessing repository {repo_name}...", progress=0.1, repo_name=repo_name)

        # If the repo exists, pull the latest changes. Otherwise, clone it fresh.
        if os.path.exists(repo_path):
            try:
                print(f"Repository {repo_name} already exists. Pulling latest changes.")
                repo = git.Repo(repo_path)
                origin = repo.remotes.origin
                origin.pull()
                # If we pull, we must re-index, so delete the old vector store.
                if os.path.exists(vector_db_path):
                    shutil.rmtree(vector_db_path)
            except Exception as e:
                print(f"Error pulling repo, attempting to re-clone. Error: {e}")
                try:
                    shutil.rmtree(repo_path) # Delete corrupted repo
                except PermissionError:
                    print(f"Permission denied when trying to delete {repo_path}. This is normal on Windows.")
                    # On Windows, we might not be able to delete immediately due to file locks
                    # Give the system a moment to release file handles
                    time.sleep(1)
                    # The next clone attempt will overwrite the directory anyway
                git.Repo.clone_from(repo_url, repo_path)
        else:
            print(f"Cloning new repository: {repo_url} into {repo_path}")
            os.makedirs(REPO_DIR, exist_ok=True)
            git.Repo.clone_from(repo_url, repo_path)

        # --- 2. INDEXING (LOADING & SPLITTING) ---
        await update_state(status="indexing", message="Parsing code files...", progress=0.4)

        loader = GenericLoader.from_filesystem(
            repo_path,
            glob="**/*",
            suffixes=[".py", ".js", ".ts", ".md", ".java", ".html", ".css"],
            parser=LanguageParser(parser_threshold=500),
        )
        documents = loader.load()

        if not documents:
            raise ValueError("No supported code files found in the repository.")

        python_splitter = RecursiveCharacterTextSplitter.from_language(language=Language.PYTHON, chunk_size=2000, chunk_overlap=200)
        js_splitter = RecursiveCharacterTextSplitter.from_language(language=Language.JS, chunk_size=2000, chunk_overlap=200)
        texts = python_splitter.split_documents(documents)
        texts.extend(js_splitter.split_documents(documents))

        print(f"Loaded {len(documents)} documents, split into {len(texts)} chunks.")

        # --- 3. EMBEDDING & STORING ---
        await update_state(status="indexing", message=f"Creating embeddings for {len(texts)} code chunks...", progress=0.7)

        Chroma.from_documents(
            texts,
            gemini_embeddings,
            persist_directory=vector_db_path
        )

        await update_state(
            status="ready",
            message="Repository successfully indexed and ready to be queried.",
            progress=1.0,
            repo_path=repo_path,
        )
        print(f"Successfully processed and indexed {repo_name}")

    except Exception as e:
        print(f"Error during repository processing: {e}")
        await update_state(status="error", message=str(e), progress=0.0)
    finally:
        # ALWAYS RELEASE THE LOCK
        await update_state(is_processing=False) 