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

        if not repo_name:
            return {"answer": "No repository is currently loaded. Please clone a repository first.", "retrieved_code": []}

        # Debug: Print what's in memory
        print(f"Current vector stores in memory: {list(VECTOR_STORES.keys())}")
        print(f"Looking for repository: {repo_name}")

        # Check if vector store exists in memory
        if repo_name not in VECTOR_STORES:
            return {"answer": f"Repository '{repo_name}' was previously loaded but the index has been cleared (likely due to server restart). Please re-clone the repository to rebuild the index.", "retrieved_code": []}

        # Get the in-memory vector store
        vectorstore = VECTOR_STORES[repo_name]
        
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

        # Enhanced Cursor-like prompt template
        template = """
You are an expert AI coding assistant similar to Cursor's AI. You have deep understanding of the codebase and can provide intelligent code suggestions, explanations, and improvements.

Repository: {repo_name}

{metadata_context}

IMPORTANT GUIDELINES (Cursor-like behavior):
1. **Code Understanding**: Analyze the code structure, patterns, and relationships
2. **Intelligent Suggestions**: Provide specific, actionable code improvements
3. **Context Awareness**: Consider the broader codebase context when answering
4. **Best Practices**: Suggest modern coding practices and patterns
5. **Error Detection**: Identify potential bugs, issues, or improvements
6. **Code Generation**: When asked, provide complete, working code examples
7. **Refactoring**: Suggest ways to improve code organization and structure
8. **Documentation**: Help explain complex code sections clearly
9. **Performance**: Suggest optimizations when relevant
10. **Security**: Point out potential security issues
11. **File Relationships**: Explain how different files work together
12. **Architecture**: Provide insights about the overall system design

Current Context:
{context}

{focus_context}

Question: {question}

Provide a comprehensive, Cursor-like response that includes:
- Clear explanation of the code
- Specific suggestions for improvements
- Code examples when helpful
- Best practices recommendations
- Any potential issues or concerns

Answer:
"""
        prompt = ChatPromptTemplate.from_template(template)

        # Enhanced context preparation
        retrieved_docs = retriever.get_relevant_documents(question)
        context = format_docs(retrieved_docs)
        
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
                "focus_context": lambda x: focus_context
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
        print(f"Error in RAG query: {e}")
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