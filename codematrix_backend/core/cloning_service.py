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
from .rag_service import store_vector_db, clear_vector_db

REPO_DIR = "repositories"

async def clone_and_process_repo(repo_url):
    try:
        # Convert to string - Pydantic HttpUrl should convert automatically
        repo_url = str(repo_url)
        print(f"Processing repository URL: {repo_url}")
        
        # SET THE LOCK
        await update_state(is_processing=True)
        
        repo_name = os.path.basename(urlparse(repo_url).path).replace('.git', '')
        repo_path = os.path.join(REPO_DIR, repo_name)

        # Clear any existing in-memory vector store for this repo
        clear_vector_db(repo_name)

        # --- 1. FRESH CLONING (ALWAYS CLEAR OLD DATA) ---
        await update_state(status="cloning", message=f"Accessing repository {repo_name}...", progress=0.1, repo_name=repo_name)

        # ALWAYS remove existing repository to ensure fresh data
        if os.path.exists(repo_path):
            try:
                print(f"Removing existing repository {repo_name} for fresh clone...")
                shutil.rmtree(repo_path)
            except PermissionError:
                print(f"Permission denied when trying to delete {repo_path}. This is normal on Windows.")
                # On Windows, we might not be able to delete immediately due to file locks
                # Give the system a moment to release file handles
                time.sleep(1)
                # Try again
                try:
                    shutil.rmtree(repo_path)
                except:
                    print(f"Could not remove {repo_path}, will overwrite during clone")

        # Always do a fresh clone
        print(f"Cloning repository: {repo_url} into {repo_path}")
        os.makedirs(REPO_DIR, exist_ok=True)
        git.Repo.clone_from(repo_url, repo_path)

        # --- 2. INDEXING (LOADING & SPLITTING) ---
        await update_state(status="indexing", message="Parsing code files...", progress=0.4)

        # Get absolute path to ensure we're loading from the right directory
        abs_repo_path = os.path.abspath(repo_path)
        print(f"Loading documents from absolute path: {abs_repo_path}")
        
        # Verify the directory exists and contains files
        if not os.path.exists(abs_repo_path):
            raise ValueError(f"Repository directory does not exist: {abs_repo_path}")
        
        # List some files to verify we're in the right place
        files = []
        for root, dirs, filenames in os.walk(abs_repo_path):
            for filename in filenames:
                if filename.endswith(('.py', '.js', '.ts', '.md', '.java', '.html', '.css')):
                    files.append(os.path.join(root, filename))
        
        print(f"Found {len(files)} code files in repository")
        if files:
            print(f"Sample files: {files[:5]}")

        loader = GenericLoader.from_filesystem(
            abs_repo_path,
            glob="**/*",
            suffixes=[".py", ".js", ".ts", ".md", ".java", ".html", ".css"],
            parser=LanguageParser(parser_threshold=500),
        )
        documents = loader.load()

        if not documents:
            raise ValueError("No supported code files found in the repository.")

        print(f"Loaded {len(documents)} documents from repository")
        
        # Debug: Show some document sources
        for i, doc in enumerate(documents[:3]):
            print(f"Document {i}: {doc.metadata.get('source', 'unknown')}")

        python_splitter = RecursiveCharacterTextSplitter.from_language(language=Language.PYTHON, chunk_size=2000, chunk_overlap=200)
        js_splitter = RecursiveCharacterTextSplitter.from_language(language=Language.JS, chunk_size=2000, chunk_overlap=200)
        texts = python_splitter.split_documents(documents)
        texts.extend(js_splitter.split_documents(documents))

        print(f"Loaded {len(documents)} documents, split into {len(texts)} chunks.")

        # --- 3. EMBEDDING & STORING IN MEMORY ---
        await update_state(status="indexing", message=f"Creating embeddings for {len(texts)} code chunks...", progress=0.7)

        # Create in-memory vector store
        vectorstore = Chroma.from_documents(
            texts,
            gemini_embeddings
        )
        
        # Store in memory instead of filesystem
        store_vector_db(repo_name, vectorstore)

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