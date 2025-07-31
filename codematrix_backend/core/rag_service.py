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

async def query_codebase(question: str, top_k: int = 5):
    """
    Performs a RAG query against the indexed codebase.
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

        # Enhanced RAG prompt template with better context handling
        template = """
        You are a senior software engineer and an expert in the codebase provided. You have access to the repository: {repo_name}

        Answer the user's question based only on the following context. If the answer is not in the context, say you don't know.
        
        IMPORTANT GUIDELINES:
        1. Be concise and direct unless the user asks for detailed information
        2. For file structure questions, provide a clear overview of file types and organization
        3. For code questions, provide relevant code snippets from the context
        4. If asked about repository structure, file types, or organization, analyze the context to provide a comprehensive overview
        5. Use your knowledge to infer file types and structure from the file paths and content in the context
        6. Don't list every single file unless specifically asked - provide summaries and patterns instead
        7. For questions about "what does it do", focus on the main functionality and purpose
        8. For questions about README files, look for documentation and project descriptions
        9. For line count questions, provide estimates based on the context provided
        10. Always be honest about what you know vs what you don't know
        11. Use the repository metadata to provide accurate statistics when available

        {metadata_context}
        Context:
        {context}

        Question: {question}

        Answer:
        """
        prompt = ChatPromptTemplate.from_template(template)

        # Create the RAG chain using LangChain Expression Language (LCEL)
        rag_chain = (
            {
                "context": retriever | format_docs, 
                "question": RunnablePassthrough(),
                "repo_name": lambda x: repo_name,
                "metadata_context": lambda x: metadata_context
            }
            | prompt
            | groq_chat
            | StrOutputParser()
        )

        # Invoke the chain and get the response
        answer = rag_chain.invoke(question)

        # Retrieve the source documents for the frontend
        retrieved_docs = retriever.get_relevant_documents(question)
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