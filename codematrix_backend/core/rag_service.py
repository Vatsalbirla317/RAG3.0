# core/rag_service.py
import os
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser

from .ai_service import gemini_embeddings, groq_chat
from .state_manager import get_state

VECTOR_DB_DIR = "vector_db"

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

        if not repo_name:
            return {"answer": "No repository is currently loaded. Please clone a repository first.", "retrieved_code": []}

        vector_db_path = os.path.join(VECTOR_DB_DIR, repo_name)
        if not os.path.exists(vector_db_path):
            return {"answer": "Vector database for this repository not found. Please re-index.", "retrieved_code": []}

        # 1. Load the existing vector store
        vectorstore = Chroma(persist_directory=vector_db_path, embedding_function=gemini_embeddings)
        retriever = vectorstore.as_retriever(search_kwargs={"k": top_k})

        # 2. Define the RAG prompt template
        template = """
        You are a senior software engineer and an expert in the codebase provided.
        Answer the user's question based only on the following context.
        If the answer is not in the context, say you don't know.
        Be concise and provide code snippets from the context if they are relevant.

        Context:
        {context}

        Question:
        {question}

        Answer:
        """
        prompt = ChatPromptTemplate.from_template(template)

        # 3. Create the RAG chain using LangChain Expression Language (LCEL)
        rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | groq_chat
            | StrOutputParser()
        )

        # 4. Invoke the chain and get the response
        answer = rag_chain.invoke(question)

        # 5. Retrieve the source documents for the frontend
        retrieved_docs = retriever.get_relevant_documents(question)
        retrieved_code = [doc.page_content for doc in retrieved_docs]

        return {"answer": answer, "retrieved_code": retrieved_code}
    except Exception as e:
        print(f"Error in RAG query: {e}")
        return {"answer": f"An error occurred while processing your question: {str(e)}", "retrieved_code": []} 