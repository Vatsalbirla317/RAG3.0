# core/rag_service.py
import os
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser

from .ai_service import gemini_embeddings, groq_chat
from .state_manager import get_state

# Use in-memory storage instead of filesystem for Render compatibility
VECTOR_STORES = {}  # In-memory storage for vector databases

def format_docs(docs):
    """Helper function to format retrieved documents into a single string."""
    return "\n\n".join(doc.page_content for doc in docs)

async def query_codebase(question: str, top_k: int = 5, current_file: str = None, cursor_position: int = None):
    """
    Performs a RAG query against the indexed codebase with Cursor-like enhancements.
    """
    try:
        current_state = await get_state()
        repo_name = current_state.get("repo_name")
        repo_path = current_state.get("repo_path")

        # Enhanced debugging
        print(f"🔍 DEBUG: Current state - repo_name: '{repo_name}', repo_path: '{repo_path}'")
        print(f"🔍 DEBUG: Full state: {current_state}")
        print(f"🔍 DEBUG: Vector stores available: {list(VECTOR_STORES.keys())}")

        # Check if we have any vector stores available
        if not VECTOR_STORES:
            print(f"❌ DEBUG: No vector stores available")
            return {"answer": "No repository is currently loaded. Please clone a repository first.", "retrieved_code": []}

        # If no repo_name in state, use the first available vector store
        if not repo_name:
            available_stores = list(VECTOR_STORES.keys())
            if available_stores:
                repo_name = available_stores[0]
                print(f"✅ DEBUG: Using first available vector store: {repo_name}")
            else:
                print(f"❌ DEBUG: No repository name in state and no vector stores")
                return {"answer": "No repository is currently loaded. Please clone a repository first.", "retrieved_code": []}

        # Debug: Print what's in memory
        print(f"Current vector stores in memory: {list(VECTOR_STORES.keys())}")
        print(f"Looking for repository: {repo_name}")

        # Check if vector store exists in memory - try exact match first, then partial match
        vectorstore = None
        if repo_name in VECTOR_STORES:
            vectorstore = VECTOR_STORES[repo_name]
            print(f"✅ DEBUG: Found exact match for repository: {repo_name}")
        else:
            # Try to find a partial match (in case repo name has timestamp suffix)
            for store_name in VECTOR_STORES.keys():
                if repo_name in store_name or store_name in repo_name:
                    vectorstore = VECTOR_STORES[store_name]
                    print(f"✅ DEBUG: Found partial match: {store_name} for {repo_name}")
                    break
        
        if not vectorstore:
            print(f"❌ DEBUG: No vector store found for repository: {repo_name}")
            print(f"❌ DEBUG: Available stores: {list(VECTOR_STORES.keys())}")
            return {"answer": f"No repository index found for '{repo_name}'. Please clone a repository first.", "retrieved_code": []}

        print(f"✅ DEBUG: Successfully found vector store for: {repo_name}")

        # Vector store already retrieved above
        
        # Enhanced retrieval strategy for Cursor-like behavior
        if current_file:
            # If we have a current file, prioritize it and related files
            retriever = vectorstore.as_retriever(search_kwargs={"k": top_k + 2})
        else:
            retriever = vectorstore.as_retriever(search_kwargs={"k": top_k})

        # Get repository metadata for better context
        repo_metadata = current_state.get("repo_metadata", {})
        metadata_context = ""
        if repo_metadata:
            metadata_context = f"""
Repository Metadata:
- Total files: {repo_metadata.get('total_files', 0)}
- Code files: {repo_metadata.get('code_files', 0)}
- Total lines of code: {repo_metadata.get('total_lines', 0)}
- File types: {', '.join([f'{ext}: {count}' for ext, count in repo_metadata.get('file_types', {}).items()])}
- Has README: {repo_metadata.get('has_readme', False)}
- Has requirements: {repo_metadata.get('has_requirements', False)}
- Has package.json: {repo_metadata.get('has_package_json', False)}

"""

        # Enhanced Cursor-like prompt template with dynamic context awareness
        template = """
You are an expert AI coding assistant similar to Cursor's AI. You have deep understanding of the codebase and can provide intelligent code suggestions, explanations, and improvements.

Repository: {repo_name}

{metadata_context}

IMPORTANT GUIDELINES (Cursor-like behavior):
1. **Direct Answers**: For simple questions (repo name, file count, etc.), give direct, concise answers
2. **Dynamic Responses**: Always base your answers on the actual repository content and context provided
3. **No Hardcoding**: Never give hardcoded responses - analyze the actual code and metadata
4. **Context Awareness**: Use the repository metadata and code context to provide accurate answers
5. **Code Understanding**: Analyze the code structure, patterns, and relationships
6. **Intelligent Suggestions**: Provide specific, actionable code improvements
7. **Best Practices**: Suggest modern coding practices and patterns
8. **Error Detection**: Identify potential bugs, issues, or improvements
9. **Code Generation**: When asked, provide complete, working code examples
10. **Refactoring**: Suggest ways to improve code organization and structure
11. **Documentation**: Help explain complex code sections clearly
12. **Performance**: Suggest optimizations when relevant
13. **Security**: Point out potential security issues
14. **File Relationships**: Explain how different files work together
15. **Architecture**: Provide insights about the overall system design

Repository Context:
{repo_context}

Code Context:
{context}

{focus_context}

Question: {question}

RESPONSE GUIDELINES:
- **For simple questions** (repo name, file count, tech stack): Give direct, one-line answers
- **For code analysis**: Provide comprehensive, Cursor-like responses based on the actual code
- **Always be dynamic**: Base every response on the actual repository content, not hardcoded information
- **Use context**: Leverage the provided code context and metadata for accurate responses
- **Be concise**: Don't over-explain simple questions

Answer:
"""
        prompt = ChatPromptTemplate.from_template(template)

        # Enhanced context preparation with better retrieval
        retrieved_docs = retriever.get_relevant_documents(question)
        context = format_docs(retrieved_docs)
        
        # Add repository-specific context for better dynamic responses
        repo_context = f"""
Repository Information:
- Name: {repo_name}
- Total Files: {repo_metadata.get('total_files', 0)}
- Code Files: {repo_metadata.get('code_files', 0)}
- File Types: {', '.join([f'{ext}: {count}' for ext, count in repo_metadata.get('file_types', {}).items()])}
- Has README: {repo_metadata.get('has_readme', False)}
- Has Requirements: {repo_metadata.get('has_requirements', False)}
- Estimated Lines: {repo_metadata.get('estimated_lines', 0)}
"""
        
        # Add focus context if we have a current file
        focus_context = ""
        if current_file:
            focus_context = f"""
FOCUS CONTEXT:
- Current file: {current_file}
- Cursor position: {cursor_position if cursor_position else 'Not specified'}
- Pay special attention to the current file and its relationships with other files in the codebase.
"""

        # Create the RAG chain using LangChain Expression Language (LCEL)
        rag_chain = (
            {
                "context": lambda x: context, 
                "question": RunnablePassthrough(),
                "repo_name": lambda x: repo_name,
                "metadata_context": lambda x: metadata_context,
                "focus_context": lambda x: focus_context,
                "repo_context": lambda x: repo_context
            }
            | prompt
            | groq_chat
            | StrOutputParser()
        )

        # Invoke the chain and get the response
        answer = rag_chain.invoke(question)

        # Retrieve the source documents for the frontend
        retrieved_code = [doc.page_content for doc in retrieved_docs]

        return {"answer": answer, "retrieved_code": retrieved_code}
    except Exception as e:
        print(f"❌ ERROR in RAG query: {e}")
        print(f"❌ ERROR details: {type(e).__name__}: {str(e)}")
        return {"answer": f"An error occurred while processing your question: {str(e)}", "retrieved_code": []}

def store_vector_db(repo_name: str, vectorstore):
    """Store vector database in memory"""
    print(f"Storing vector database for repository: {repo_name}")
    VECTOR_STORES[repo_name] = vectorstore
    print(f"Current vector stores: {list(VECTOR_STORES.keys())}")

def get_vector_db(repo_name: str):
    """Get vector database from memory"""
    return VECTOR_STORES.get(repo_name)

def clear_vector_db(repo_name: str):
    """Clear vector database from memory"""
    if repo_name in VECTOR_STORES:
        print(f"Clearing vector database for repository: {repo_name}")
        del VECTOR_STORES[repo_name]
        print(f"Current vector stores after clearing: {list(VECTOR_STORES.keys())}")

def clear_all_vector_dbs():
    """Clear all vector databases from memory"""
    print(f"Clearing all vector databases. Previous stores: {list(VECTOR_STORES.keys())}")
    VECTOR_STORES.clear()
    print("All vector databases cleared")

def get_vector_store_info():
    """Get information about current vector stores"""
    return {
        "stores": list(VECTOR_STORES.keys()),
        "count": len(VECTOR_STORES)
    } 