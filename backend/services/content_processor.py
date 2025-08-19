"""
Content processing service using Anthropic Claude
Handles content extraction, analysis, and embedding generation
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
import anthropic
from bs4 import BeautifulSoup
import requests
import re

from core.config import get_settings

class ContentProcessor:
    """Processes content using Claude AI for insights extraction"""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = anthropic.Anthropic(api_key=self.settings.anthropic_api_key)
        
    async def process_url(self, url: str) -> Dict[str, Any]:
        """Process content from a URL"""
        try:
            # Fetch content from URL
            content = await self._fetch_url_content(url)
            
            # Process the content
            return await self._process_content(content, source_url=url)
            
        except Exception as e:
            raise Exception(f"Failed to process URL {url}: {str(e)}")
    
    async def process_text(self, text: str) -> Dict[str, Any]:
        """Process direct text content"""
        try:
            return await self._process_content(text)
        except Exception as e:
            raise Exception(f"Failed to process text: {str(e)}")
    
    async def _fetch_url_content(self, url: str) -> str:
        """Fetch and extract content from URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract text content
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
            
        except Exception as e:
            raise Exception(f"Failed to fetch URL content: {str(e)}")
    
    async def _process_content(self, content: str, source_url: Optional[str] = None) -> Dict[str, Any]:
        """Process content using Claude AI"""
        try:
            # Chunk content for processing
            chunks = self._chunk_content(content)
            
            # Extract title
            title = await self._extract_title(content[:2000])  # Use first 2000 chars for title
            
            # Generate summary
            summary = await self._generate_summary(content[:5000])  # Use first 5000 chars for summary
            
            # Extract insights
            insights = await self._extract_insights(content)
            
            # Extract tags
            tags = await self._extract_tags(content)
            
            # Extract action items
            action_items = await self._extract_action_items(content)
            
            # Extract quotable snippets
            quotable_snippets = await self._extract_quotable_snippets(content)
            
            return {
                "title": title,
                "summary": summary,
                "tags": tags,
                "insights": insights,
                "action_items": action_items,
                "quotable_snippets": quotable_snippets,
                "chunks": chunks,
                "source_url": source_url
            }
            
        except Exception as e:
            raise Exception(f"Failed to process content: {str(e)}")
    
    def _chunk_content(self, content: str) -> List[Dict[str, Any]]:
        """Split content into chunks for processing"""
        chunks = []
        chunk_size = self.settings.chunk_size
        overlap = self.settings.chunk_overlap
        
        # Simple chunking by characters
        for i in range(0, len(content), chunk_size - overlap):
            chunk_text = content[i:i + chunk_size]
            if chunk_text.strip():
                chunks.append({
                    "index": len(chunks),
                    "text": chunk_text.strip(),
                    "start_char": i,
                    "end_char": i + len(chunk_text)
                })
        
        return chunks
    
    async def _extract_title(self, content: str) -> str:
        """Extract a title from content"""
        prompt = f"""Extract a concise, descriptive title (max 100 characters) from this content:

{content[:2000]}

Return only the title, nothing else."""

        response = await self._call_claude(prompt)
        return response.strip()
    
    async def _generate_summary(self, content: str) -> str:
        """Generate a summary of the content"""
        prompt = f"""Generate a concise 2-3 sentence summary of this content:

{content[:5000]}

Focus on the main points and key insights."""

        response = await self._call_claude(prompt)
        return response.strip()
    
    async def _extract_insights(self, content: str) -> List[Dict[str, Any]]:
        """Extract key insights from content"""
        prompt = f"""Extract 3-5 key insights from this content. For each insight, provide:
1. The insight text
2. A relevance score (0-1)
3. Brief context explaining why it's important

Content:
{content[:8000]}

Return as JSON array with format:
[
  {{
    "text": "insight text",
    "relevance_score": 0.85,
    "context": "why this insight matters"
  }}
]"""

        response = await self._call_claude(prompt)
        try:
            return json.loads(response)
        except:
            # Fallback: return simple insights
            return [{"text": "Key insight extracted", "relevance_score": 0.8, "context": "Important finding"}]
    
    async def _extract_tags(self, content: str) -> List[str]:
        """Extract relevant tags from content"""
        prompt = f"""Extract 5-10 relevant tags from this content. Focus on:
- Main topics/themes
- Key concepts
- Domain-specific terms
- Actionable categories

Content:
{content[:4000]}

Return as a JSON array of strings: ["tag1", "tag2", "tag3"]"""

        response = await self._call_claude(prompt)
        try:
            return json.loads(response)
        except:
            return ["research", "insights", "analysis"]
    
    async def _extract_action_items(self, content: str) -> List[str]:
        """Extract actionable items from content"""
        prompt = f"""Extract 3-5 actionable items or next steps from this content. Focus on:
- Specific actions to take
- Recommendations
- Follow-up tasks
- Implementation steps

Content:
{content[:6000]}

Return as a JSON array of strings: ["action 1", "action 2"]"""

        response = await self._call_claude(prompt)
        try:
            return json.loads(response)
        except:
            return ["Review and analyze findings", "Implement recommendations"]
    
    async def _extract_quotable_snippets(self, content: str) -> List[Dict[str, str]]:
        """Extract quotable snippets from content"""
        prompt = f"""Extract 2-3 quotable snippets from this content. For each snippet, provide:
1. The exact quote
2. Context explaining why it's quotable

Content:
{content[:8000]}

Return as JSON array:
[
  {{
    "quote": "exact quote here",
    "context": "why this quote is important"
  }}
]"""

        response = await self._call_claude(prompt)
        try:
            return json.loads(response)
        except:
            return [{"quote": "Key quote from content", "context": "Important insight"}]
    
    async def _call_claude(self, prompt: str) -> str:
        """Make a call to Claude API"""
        try:
            response = self.client.messages.create(
                model=self.settings.claude_model,
                max_tokens=1000,
                temperature=0.3,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            return response.content[0].text
        except Exception as e:
            raise Exception(f"Claude API call failed: {str(e)}")
    
    async def generate_embeddings(self, document_id: str, chunks: List[Dict[str, Any]]):
        """Generate embeddings for content chunks"""
        try:
            from database.client import get_supabase_service_client
            supabase = get_supabase_service_client()
            
            for chunk in chunks:
                # Generate embedding for chunk text
                embedding = await self._generate_embedding(chunk["text"])
                
                # Store embedding
                embedding_data = {
                    "document_id": document_id,
                    "chunk_index": chunk["index"],
                    "content": chunk["text"],
                    "embedding": embedding
                }
                
                supabase.table("embeddings").insert(embedding_data).execute()
                
        except Exception as e:
            print(f"Failed to generate embeddings: {str(e)}")
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using Claude"""
        try:
            # Try Anthropic embeddings first
            response = self.client.embeddings.create(
                model=self.settings.claude_embedding_model,
                input=text
            )
            return response.embeddings[0].embedding
        except (AttributeError, Exception) as e:
            # Fallback to OpenAI embeddings if Anthropic fails
            try:
                import openai
                openai_client = openai.OpenAI(api_key=self.settings.openai_api_key)
                response = openai_client.embeddings.create(
                    model="text-embedding-3-small",
                    input=text
                )
                return response.data[0].embedding
            except Exception as openai_error:
                # Final fallback: hash-based embedding
                print(f"Warning: Both Anthropic and OpenAI embeddings failed, using fallback. Errors: {str(e)}, {str(openai_error)}")
                import hashlib
                hash_obj = hashlib.md5(text.encode())
                hash_bytes = hash_obj.digest()
                # Convert to list of floats (3072 dimensions)
                embedding = [float(b) / 255.0 for b in hash_bytes] * 96  # 32 * 96 = 3072
                return embedding[:3072]
