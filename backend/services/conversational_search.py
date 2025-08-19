"""
Conversational Search Service
Provides conversational responses based on search results
"""

import anthropic
from typing import List, Dict, Any, Optional
from core.config import get_settings
import logging

logger = logging.getLogger(__name__)

class ConversationalSearchService:
    """Service for providing conversational responses to search queries"""
    
    def __init__(self):
        settings = get_settings()
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.model = "claude-3-5-sonnet-20241022"
    
    async def get_conversational_response(
        self, 
        query: str, 
        search_results: List[Dict[str, Any]],
        max_results: int = 5
    ) -> Dict[str, Any]:
        """
        Generate a conversational response based on search results
        
        Args:
            query: User's search query
            search_results: List of search result documents
            max_results: Maximum number of results to include in response
            
        Returns:
            Dict containing conversational response and metadata
        """
        try:
            if not search_results:
                return {
                    'response': f"I couldn't find any relevant information about '{query}' in your documents. Try rephrasing your question or adding more content to your library.",
                    'sources': [],
                    'confidence': 0.0,
                    'suggestions': [
                        "Try using different keywords",
                        "Check if you have relevant documents in your library",
                        "Consider adding more content related to your query"
                    ]
                }
            
            # Limit results for processing
            top_results = search_results[:max_results]
            
            # Prepare context from search results
            context = self._prepare_context(top_results)
            
            # Generate conversational response
            response = await self._generate_response(query, context, top_results)
            
            # Calculate confidence based on result quality
            confidence = self._calculate_confidence(top_results)
            
            # Generate follow-up suggestions
            suggestions = await self._generate_suggestions(query, top_results)
            
            return {
                'response': response,
                'sources': [{
                    'title': result.get('document_title', 'Unknown'),
                    'url': result.get('document_url', ''),
                    'relevance': result.get('similarity', 0.0),
                    'content_preview': result.get('content', '')[:200] + '...' if result.get('content') else ''
                } for result in top_results],
                'confidence': confidence,
                'suggestions': suggestions,
                'result_count': len(search_results),
                'query': query
            }
            
        except Exception as e:
            logger.error(f"Error generating conversational response: {str(e)}")
            return {
                'response': f"I encountered an error while processing your query about '{query}'. Please try again.",
                'sources': [],
                'confidence': 0.0,
                'suggestions': ["Try rephrasing your question", "Check your internet connection"],
                'error': str(e)
            }
    
    def _prepare_context(self, search_results: List[Dict[str, Any]]) -> str:
        """
        Prepare context from search results for AI processing
        
        Args:
            search_results: List of search result documents
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        for i, result in enumerate(search_results, 1):
            title = result.get('document_title', 'Unknown Document')
            content = result.get('content', '')
            relevance = result.get('similarity', 0.0)
            
            context_parts.append(f"""
Document {i}: {title}
Relevance Score: {relevance:.2f}
Content: {content}
---""")
        
        return '\n'.join(context_parts)
    
    async def _generate_response(
        self, 
        query: str, 
        context: str, 
        search_results: List[Dict[str, Any]]
    ) -> str:
        """
        Generate conversational response using Claude
        
        Args:
            query: User's search query
            context: Prepared context from search results
            search_results: Original search results for reference
            
        Returns:
            Generated conversational response
        """
        try:
            # Create prompt for conversational response
            prompt = f"""You are a helpful research assistant. Based on the following documents, provide a conversational response to the user's query.

User Query: {query}

Relevant Documents:
{context}

Instructions:
1. Provide a natural, conversational response that directly answers the user's question
2. Synthesize information from multiple documents when relevant
3. Be specific and cite information from the documents
4. If the documents don't fully answer the question, acknowledge this
5. Use a helpful, informative tone
6. Keep the response concise but comprehensive (2-4 paragraphs)

Response:"""

            # Generate response using Claude
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0.3,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            return f"I found some relevant information about '{query}', but I encountered an error while generating a response. Here are the key documents I found: {', '.join([r.get('document_title', 'Unknown') for r in search_results[:3]])}"
    
    def _calculate_confidence(self, search_results: List[Dict[str, Any]]) -> float:
        """
        Calculate confidence score based on search result quality
        
        Args:
            search_results: List of search result documents
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        if not search_results:
            return 0.0
        
        # Calculate average relevance score
        avg_relevance = sum(r.get('similarity', 0.0) for r in search_results) / len(search_results)
        
        # Factor in number of results (more results = higher confidence)
        result_factor = min(len(search_results) / 5.0, 1.0)
        
        # Factor in top result quality (high top score = higher confidence)
        top_score = search_results[0].get('similarity', 0.0) if search_results else 0.0
        
        # Weighted combination
        confidence = (avg_relevance * 0.4) + (result_factor * 0.3) + (top_score * 0.3)
        
        return min(confidence, 1.0)
    
    async def _generate_suggestions(
        self, 
        query: str, 
        search_results: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Generate follow-up suggestions based on search results
        
        Args:
            query: Original user query
            search_results: Search result documents
            
        Returns:
            List of suggested follow-up questions
        """
        try:
            if not search_results:
                return [
                    "Try using different keywords",
                    "Check if you have relevant documents in your library",
                    "Consider adding more content related to your query"
                ]
            
            # Extract key topics from search results
            topics = set()
            for result in search_results[:3]:  # Use top 3 results
                title = result.get('document_title', '').lower()
                content = result.get('content', '').lower()
                
                # Simple topic extraction (in a real implementation, you'd use more sophisticated NLP)
                words = (title + ' ' + content).split()
                topics.update([word for word in words if len(word) > 4 and word.isalpha()])
            
            # Generate suggestions based on topics and query
            suggestions = []
            
            if 'reading' in query.lower() and 'writing' in query.lower():
                suggestions.extend([
                    "How does reading improve writing skills?",
                    "What are the best practices for reading to enhance writing?",
                    "Can you explain the relationship between critical thinking and writing?"
                ])
            elif 'reading' in query.lower():
                suggestions.extend([
                    "What are effective reading strategies?",
                    "How can I improve my reading comprehension?",
                    "What types of reading materials are most beneficial?"
                ])
            elif 'writing' in query.lower():
                suggestions.extend([
                    "What are the key elements of good writing?",
                    "How can I develop my writing style?",
                    "What are common writing mistakes to avoid?"
                ])
            else:
                # Generic suggestions based on found topics
                topic_list = list(topics)[:3]
                if topic_list:
                    suggestions.extend([
                        f"Tell me more about {topic_list[0]}",
                        f"How does {topic_list[0]} relate to {topic_list[1] if len(topic_list) > 1 else 'other topics'}?",
                        "What are the key insights from these documents?"
                    ])
            
            # Add general suggestions
            suggestions.extend([
                "Can you summarize the main points from these documents?",
                "What are the practical applications of this information?"
            ])
            
            return suggestions[:5]  # Limit to 5 suggestions
            
        except Exception as e:
            logger.error(f"Error generating suggestions: {str(e)}")
            return [
                "Try rephrasing your question",
                "Search for related topics",
                "Check your document library for more content"
            ]
    
    async def get_enhanced_search_response(
        self, 
        query: str, 
        search_service_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enhanced search that combines search results with conversational response
        
        Args:
            query: User's search query
            search_service_results: Results from the search service
            
        Returns:
            Enhanced response with conversational elements
        """
        try:
            # Extract search results
            results = search_service_results.get('results', [])
            
            # Get conversational response
            conversational_response = await self.get_conversational_response(query, results)
            
            # Combine with original search metadata
            enhanced_response = {
                **conversational_response,
                'search_metadata': {
                    'total_results': search_service_results.get('total_count', 0),
                    'search_type': search_service_results.get('search_type', 'keyword'),
                    'query': search_service_results.get('query', query)
                },
                'raw_results': results  # Include raw results for reference
            }
            
            return enhanced_response
            
        except Exception as e:
            logger.error(f"Error in enhanced search response: {str(e)}")
            return {
                'response': f"I found some information about '{query}', but encountered an error while processing the results.",
                'sources': [],
                'confidence': 0.0,
                'suggestions': ["Try again", "Check your query"],
                'error': str(e)
            }
