# core/cloning_service.py
import os
import git
import shutil
import time
import tempfile
import asyncio
from urllib.parse import urlparse

from langchain.text_splitter import Language, RecursiveCharacterTextSplitter
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain_community.vectorstores import Chroma

from .state_manager import update_state
from .ai_service import gemini_embeddings
from .rag_service import store_vector_db, clear_vector_db

# Use a temporary directory that's more likely to work on Render
REPO_DIR = os.path.join(tempfile.gettempdir(), "codematrix_repos")

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

        # Create the repositories directory
        os.makedirs(REPO_DIR, exist_ok=True)
        print(f"Created repository directory: {REPO_DIR}")
        
        # ALWAYS remove existing repository to ensure fresh data
        if os.path.exists(repo_path):
            try:
                print(f"Removing existing repository {repo_name} for fresh clone...")
                shutil.rmtree(repo_path)
            except (PermissionError, OSError) as e:
                print(f"Could not remove {repo_path}: {e}")
                # Try to use a different directory name
                repo_path = os.path.join(REPO_DIR, f"{repo_name}_{int(time.time())}")
                print(f"Using alternative path: {repo_path}")

        # Try different cloning approaches with timeout
        clone_success = False
        clone_error = None
        
        # Method 1: Standard clone with timeout
        try:
            print(f"Attempting standard clone: {repo_url} into {repo_path}")
            
            # Run git clone with timeout
            def clone_repo():
                return git.Repo.clone_from(repo_url, repo_path, depth=1)
            
            # Use asyncio to add timeout
            try:
                loop = asyncio.get_event_loop()
                await asyncio.wait_for(loop.run_in_executor(None, clone_repo), timeout=60.0)
                clone_success = True
                print("Standard clone successful!")
            except asyncio.TimeoutError:
                print("Standard clone timed out after 60 seconds")
                clone_error = "Clone timed out"
                
        except Exception as e:
            print(f"Standard clone failed: {e}")
            clone_error = str(e)
            
            # Method 2: Try with different options
            if not clone_success:
                try:
                    print(f"Attempting clone with different options...")
                    
                    def clone_repo_alt():
                        return git.Repo.clone_from(
                            repo_url, 
                            repo_path, 
                            depth=1,
                            single_branch=True,
                            no_checkout=False
                        )
                    
                    try:
                        await asyncio.wait_for(loop.run_in_executor(None, clone_repo_alt), timeout=60.0)
                        clone_success = True
                        print("Alternative clone successful!")
                    except asyncio.TimeoutError:
                        print("Alternative clone timed out after 60 seconds")
                        clone_error = "Alternative clone timed out"
                        
                except Exception as e2:
                    print(f"Alternative clone also failed: {e2}")
                    clone_error = str(e2)
                    
                    # Method 3: Try in a completely different location
                    if not clone_success:
                        try:
                            alt_path = os.path.join(tempfile.gettempdir(), f"repo_{int(time.time())}")
                            print(f"Trying alternative location: {alt_path}")
                            
                            def clone_repo_alt2():
                                return git.Repo.clone_from(repo_url, alt_path, depth=1)
                            
                            try:
                                await asyncio.wait_for(loop.run_in_executor(None, clone_repo_alt2), timeout=60.0)
                                repo_path = alt_path
                                clone_success = True
                                print("Alternative location clone successful!")
                            except asyncio.TimeoutError:
                                print("Alternative location clone timed out")
                                clone_error = "All cloning methods timed out"
                                
                        except Exception as e3:
                            print(f"All cloning methods failed: {e3}")
                            clone_error = str(e3)

        if not clone_success:
            error_msg = f"Failed to clone repository after multiple attempts: {clone_error}"
            print(error_msg)
            raise Exception(error_msg)

        # --- 2. INDEXING (LOADING & SPLITTING) ---
        await update_state(status="indexing", message="Parsing code files...", progress=0.4)

        # Get absolute path to ensure we're loading from the right directory
        abs_repo_path = os.path.abspath(repo_path)
        print(f"Loading documents from absolute path: {abs_repo_path}")
        
        # Verify the directory exists and contains files
        if not os.path.exists(abs_repo_path):
            raise ValueError(f"Repository directory does not exist: {abs_repo_path}")
        
        # List ALL files in the repository for debugging (but don't print all)
        all_files = []
        for root, dirs, filenames in os.walk(abs_repo_path):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                all_files.append(file_path)
        
        print(f"TOTAL files found in repository: {len(all_files)}")
        # Only show first few files to avoid spam
        if len(all_files) <= 10:
            print(f"Files: {all_files}")
        else:
            print(f"Files: {all_files[:5]}... and {len(all_files)-5} more")
        
        # List some files to verify we're in the right place
        files = []
        for root, dirs, filenames in os.walk(abs_repo_path):
            for filename in filenames:
                if filename.endswith(('.py', '.js', '.ts', '.md', '.java', '.html', '.css')):
                    files.append(os.path.join(root, filename))
        
        print(f"Found {len(files)} code files in repository (filtered by extension)")
        if files:
            print(f"Code files: {files}")
        else:
            print("WARNING: No code files found with supported extensions!")

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
        
        # Debug: Show some document sources (but not content previews to reduce spam)
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

        # Collect repository metadata for better analysis
        repo_metadata = await collect_repository_metadata(repo_path, texts)
        
        await update_state(
            status="ready",
            message="Repository successfully indexed and ready to be queried.",
            progress=1.0,
            repo_path=repo_path,
            repo_metadata=repo_metadata
        )
        print(f"Successfully processed and indexed {repo_name}")

    except Exception as e:
        print(f"Error during repository processing: {e}")
        await update_state(status="error", message=str(e), progress=0.0)
    finally:
        # ALWAYS RELEASE THE LOCK
        await update_state(is_processing=False)

async def collect_repository_metadata(repo_path: str, texts: list) -> dict:
    """Collect comprehensive metadata about the repository"""
    try:
        metadata = {
            "total_files": 0,
            "code_files": 0,
            "file_types": {},
            "total_lines": 0,
            "languages": set(),
            "has_readme": False,
            "has_requirements": False,
            "has_package_json": False,
            "main_files": []
        }
        
        # Count files and collect metadata
        for root, dirs, filenames in os.walk(repo_path):
            for filename in filenames:
                metadata["total_files"] += 1
                file_path = os.path.join(root, filename)
                file_ext = os.path.splitext(filename)[1].lower()
                
                # Track file types
                if file_ext:
                    metadata["file_types"][file_ext] = metadata["file_types"].get(file_ext, 0) + 1
                
                # Check for specific important files
                if filename.lower() in ['readme.md', 'readme.txt', 'readme']:
                    metadata["has_readme"] = True
                elif filename.lower() in ['requirements.txt', 'pyproject.toml', 'setup.py']:
                    metadata["has_requirements"] = True
                elif filename.lower() == 'package.json':
                    metadata["has_package_json"] = True
                
                # Count code files
                if file_ext in ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.go', '.rs', '.php', '.rb']:
                    metadata["code_files"] += 1
                    # Estimate lines of code (rough estimate)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                            metadata["total_lines"] += len(lines)
                    except (UnicodeDecodeError, PermissionError, FileNotFoundError) as e:
                        # Skip files that can't be read (binary files, permission issues, etc.)
                        print(f"⚠️ Could not read file {file_path}: {e}")
                        continue
                    except Exception as e:
                        print(f"⚠️ Unexpected error reading file {file_path}: {e}")
                        continue
        
        # Convert set to list for JSON serialization
        metadata["languages"] = list(metadata["languages"])
        
        # Estimate total lines from text chunks
        metadata["estimated_lines"] = len(texts) * 50  # Rough estimate
        
        print(f"Repository metadata collected: {metadata}")
        return metadata
        
    except Exception as e:
        print(f"Error collecting repository metadata: {e}")
        return {} 