import os
import asyncio
from typing import List, Optional
import groq
import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_groq import ChatGroq
from .config import settings

class AIService:
    def __init__(self):
        self.groq_client = None
        self.gemini_model = None
        self.gemini_embeddings = None
        self.groq_chat = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize AI clients based on available API keys"""
        try:
            # Initialize Groq client
            if settings.has_groq_key:
                self.groq_client = groq.Groq(api_key=settings.GROQ_API_KEY)
                print("✅ Groq client initialized successfully")
            else:
                print("⚠️ Groq API key not configured")
            
            # Initialize Gemini client
            if settings.has_gemini_keys:
                genai.configure(api_key=settings.GEMINI_API_KEY_1 or settings.GEMINI_API_KEY_2)
                self.gemini_model = genai.GenerativeModel('gemini-pro')
                print("✅ Gemini client initialized successfully")
            else:
                print("⚠️ Gemini API keys not configured")
            
            # Initialize Gemini Embeddings
            if settings.has_gemini_keys:
                self.gemini_embeddings = GoogleGenerativeAIEmbeddings(
                    model="models/text-embedding-004",
                    google_api_key=settings.google_api_key
                )
                print("✅ Gemini embeddings initialized successfully")
            
            # Initialize Groq Chat for LangChain
            if settings.has_groq_key:
                self.groq_chat = ChatGroq(
                    api_key=settings.GROQ_API_KEY,
                    model="llama3-8b-8192"
                )
                print("✅ Groq Chat initialized successfully")
                
            if not settings.has_any_ai_key:
                print("❌ No AI API keys configured - some features may not work")
                
        except Exception as e:
            print(f"❌ Error initializing AI clients: {e}")
            # Continue with partial initialization
    
    async def chat_completion(
        self, 
        messages: List[dict], 
        model: str = "groq",
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> str:
        """Generate chat completion using specified model"""
        try:
            if model == "groq" and self.groq_client:
                return await self._groq_completion(messages, temperature, max_tokens)
            elif model == "gemini" and self.gemini_model:
                return await self._gemini_completion(messages, temperature, max_tokens)
            else:
                raise ValueError(f"Model {model} not available or not configured")
        except Exception as e:
            raise Exception(f"AI completion failed: {str(e)}")
    
    async def _groq_completion(
        self, 
        messages: List[dict], 
        temperature: float, 
        max_tokens: int
    ) -> str:
        """Generate completion using Groq API"""
        try:
            response = self.groq_client.chat.completions.create(
                model="llama3-8b-8192",
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=1,
                stream=False
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Groq API error: {str(e)}")
    
    async def _gemini_completion(
        self, 
        messages: List[dict], 
        temperature: float, 
        max_tokens: int
    ) -> str:
        """Generate completion using Gemini API"""
        try:
            # Convert messages to Gemini format
            gemini_messages = []
            for msg in messages:
                if msg["role"] == "user":
                    gemini_messages.append({"role": "user", "parts": [msg["content"]]})
                elif msg["role"] == "assistant":
                    gemini_messages.append({"role": "model", "parts": [msg["content"]]})
            
            response = self.gemini_model.generate_content(
                gemini_messages,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                )
            )
            return response.text
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    async def explain_code(
        self, 
        code: str, 
        complexity: str = "adult",
        model: str = "groq"
    ) -> str:
        """Explain code at specified complexity level"""
        complexity_prompts = {
            "5-year-old": "Explain this code like I'm a 5-year-old child. Use simple words and analogies.",
            "10-year-old": "Explain this code like I'm a 10-year-old. Use simple terms but include basic programming concepts.",
            "teenager": "Explain this code like I'm a teenager learning programming. Include technical details but keep it accessible.",
            "adult": "Explain this code for an adult programmer. Include technical details and best practices."
        }
        
        prompt = f"""
        {complexity_prompts.get(complexity, complexity_prompts["adult"])}
        
        Code to explain:
        ```python
        {code}
        ```
        
        Please provide a clear, well-structured explanation.
        """
        
        messages = [{"role": "user", "content": prompt}]
        return await self.chat_completion(messages, model)
    
    async def generate_chat_response(
        self, 
        question: str, 
        context: Optional[str] = None,
        model: str = "groq"
    ) -> str:
        """Generate chat response with optional context"""
        if context:
            prompt = f"""
            Context from codebase:
            {context}
            
            User question: {question}
            
            Please provide a helpful answer based on the context provided.
            """
        else:
            prompt = f"User question: {question}\n\nPlease provide a helpful answer."
        
        messages = [{"role": "user", "content": prompt}]
        return await self.chat_completion(messages, model)

    async def chat(self, prompt: str, model: str = "groq") -> str:
        """Simple chat method for direct prompt responses"""
        messages = [{"role": "user", "content": prompt}]
        return await self.chat_completion(messages, model)

# Global AI service instance
ai_service = AIService()

# Initialize the Gemini Embedding Model (for direct access)
gemini_embeddings = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004",
    google_api_key=settings.google_api_key
) if settings.has_gemini_keys else None

# Initialize the Groq Chat Model (for later use)
groq_chat = ChatGroq(
    api_key=settings.GROQ_API_KEY,
    model="llama3-8b-8192"
) if settings.has_groq_key else None

print("AI services initialized.") 