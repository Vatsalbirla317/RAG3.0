#!/usr/bin/env python3
"""
Test script for the RAG pipeline
"""
import asyncio
import os
from core.rag_service import query_codebase
from core.state_manager import update_state

async def test_rag_pipeline():
    """Test the RAG pipeline with a mock repository"""
    
    print("🧪 Testing RAG Pipeline...")
    
    # Test 1: No repository loaded
    print("\n1. Testing with no repository loaded...")
    response = await query_codebase("What is the main function?")
    print(f"Response: {response['answer']}")
    
    # Test 2: Mock repository state
    print("\n2. Testing with mock repository state...")
    await update_state(
        status="ready",
        message="Test repository loaded",
        progress=1.0,
        repo_name="test-repo"
    )
    
    response = await query_codebase("What is the main function?")
    print(f"Response: {response['answer']}")
    
    print("\n✅ RAG pipeline test completed!")

if __name__ == "__main__":
    asyncio.run(test_rag_pipeline()) 