"""
LLM service for generating answers.
"""
from typing import List, Dict, Any, AsyncIterator, Union
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
from app.config import settings


class LLMService:
    """Service for LLM interactions."""
    
    def __init__(self):
        """Initialize LLM client."""
        self.provider = settings.LLM_PROVIDER
        
        if self.provider == "openai":
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = settings.OPENAI_LLM_MODEL
        elif self.provider == "anthropic":
            self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
            self.model = "claude-3-opus-20240229"
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    async def generate_answer(
        self,
        query: str,
        context_chunks: List[Dict[str, Any]],
        stream: bool = False
    ):
        """Generate answer from query and context."""
        # Build context from chunks
        context_text = "\n\n".join([
            f"[Source: {chunk.get('source_name', 'Unknown')}]\n{chunk.get('text', '')}"
            for chunk in context_chunks
        ])
        
        system_prompt = """You are a helpful AI assistant with access to a user's personal knowledge base.
Your task is to answer questions based on the provided context. Be concise, accurate, and cite sources when relevant.
If the context doesn't contain enough information to answer the question, say so clearly."""
        
        user_prompt = f"""Context from knowledge base:
{context_text}

Question: {query}

Please provide a comprehensive answer based on the context above."""
        
        if self.provider == "openai":
            if stream:
                # For streaming, return the async generator directly (it's already a coroutine)
                # We'll await it in the calling code
                return self._stream_openai(system_prompt, user_prompt)
            else:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7
                )
                return response.choices[0].message.content
        else:  # anthropic
            if stream:
                return self._stream_anthropic(system_prompt, user_prompt)
            else:
                message = await self.client.messages.create(
                    model=self.model,
                    max_tokens=1024,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}]
                )
                return message.content[0].text
    
    async def _stream_openai(self, system_prompt: str, user_prompt: str) -> AsyncIterator[str]:
        """Stream response from OpenAI."""
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            stream=True
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    async def _stream_anthropic(self, system_prompt: str, user_prompt: str) -> AsyncIterator[str]:
        """Stream response from Anthropic."""
        async with self.client.messages.stream(
            model=self.model,
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        ) as stream:
            async for text in stream.text_stream:
                yield text


llm_service = LLMService()

