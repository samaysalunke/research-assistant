"""
Enhanced Conversational Search Service
Provides advanced conversational responses with multi-turn conversations and context management
"""

import anthropic
import uuid
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from core.config import get_settings
from database.client import get_supabase_service_client
import logging
import json

logger = logging.getLogger(__name__)

class EnhancedConversationalService:
    """Enhanced service for conversational responses with multi-turn conversations"""
    
    def __init__(self):
        settings = get_settings()
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.model = "claude-3-5-sonnet-20241022"
        self.supabase = get_supabase_service_client()
        self.max_context_length = 8000  # Maximum context length for Claude
        self.session_timeout = timedelta(hours=2)  # Session timeout
    
    async def start_conversation(self, user_id: str) -> Dict[str, Any]:
        """
        Start a new conversation session
        
        Args:
            user_id: User identifier
            
        Returns:
            Conversation session data
        """
        try:
            session_id = str(uuid.uuid4())
            now = datetime.utcnow()
            
            session_data = {
                "session_id": session_id,
                "user_id": user_id,
                "created_at": now.isoformat(),
                "last_activity": now.isoformat(),
                "message_count": 0,
                "context_documents": [],
                "conversation_summary": None
            }
            
            # Store session in database
            self.supabase.table("conversation_sessions").insert(session_data).execute()
            
            return {
                "session_id": session_id,
                "status": "started",
                "message": "New conversation started"
            }
            
        except Exception as e:
            logger.error(f"Error starting conversation: {str(e)}")
            return {
                "session_id": None,
                "status": "error",
                "message": f"Failed to start conversation: {str(e)}"
            }
    
    async def get_conversation_history(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get conversation history for a session
        
        Args:
            session_id: Conversation session ID
            
        Returns:
            List of conversation messages
        """
        try:
            result = self.supabase.table("conversation_messages").select("*").eq("session_id", session_id).order("timestamp", desc=False).execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error getting conversation history: {str(e)}")
            return []
    
    async def process_conversational_query(
        self,
        query: str,
        user_id: str,
        conversation_id: Optional[str] = None,
        context_documents: Optional[List[str]] = None,
        response_type: str = "comprehensive",
        include_sources: bool = True,
        max_sources: int = 5
    ) -> Dict[str, Any]:
        """
        Process a conversational query with enhanced features
        
        Args:
            query: User's question
            user_id: User identifier
            conversation_id: Optional conversation ID for multi-turn
            context_documents: Specific documents to focus on
            response_type: Type of response desired
            include_sources: Whether to include sources
            max_sources: Maximum number of sources
            
        Returns:
            Enhanced conversational response
        """
        try:
            # Handle conversation session
            if not conversation_id:
                # Start new conversation
                session_result = await self.start_conversation(user_id)
                conversation_id = session_result.get("session_id")
                if not conversation_id:
                    raise Exception("Failed to create conversation session")
            else:
                # Update session activity
                self.supabase.table("conversation_sessions").update({
                    "last_activity": datetime.utcnow().isoformat()
                }).eq("session_id", conversation_id).execute()
            
            # Analyze query intent
            query_analysis = await self._analyze_query_intent(query)
            
            # Get relevant documents
            search_results = await self._get_relevant_documents(
                query, user_id, context_documents, max_sources
            )
            
            # Get conversation history for context
            conversation_history = await self.get_conversation_history(conversation_id)
            
            # Generate enhanced response
            response = await self._generate_enhanced_response(
                query, search_results, conversation_history, response_type, query_analysis
            )
            
            # Store message in conversation history
            await self._store_conversation_message(
                conversation_id, query, response["response"], search_results, response["confidence"]
            )
            
            # Update session with new context documents
            await self._update_session_context(conversation_id, search_results)
            
            # Prepare response
            return {
                "response": response["response"],
                "conversation_id": conversation_id,
                "sources": search_results[:max_sources] if include_sources else [],
                "confidence": response["confidence"],
                "suggestions": response["suggestions"],
                "response_type": response_type,
                "metadata": {
                    "total_sources": len(search_results),
                    "conversation_length": len(conversation_history) + 1,
                    "query_complexity": query_analysis.get("complexity", "medium"),
                    "processing_time": response.get("processing_time", 0)
                },
                "query_analysis": query_analysis
            }
            
        except Exception as e:
            logger.error(f"Error processing conversational query: {str(e)}")
            return {
                "response": f"I encountered an error while processing your query: {str(e)}",
                "conversation_id": conversation_id,
                "sources": [],
                "confidence": 0.0,
                "suggestions": ["Try rephrasing your question", "Check your internet connection"],
                "response_type": response_type,
                "metadata": {},
                "query_analysis": {},
                "error": str(e)
            }
    
    async def _analyze_query_intent(self, query: str) -> Dict[str, Any]:
        """
        Analyze the intent and characteristics of a query
        
        Args:
            query: User's query
            
        Returns:
            Query analysis results
        """
        try:
            # Simple intent detection (in a real implementation, you'd use more sophisticated NLP)
            query_lower = query.lower()
            
            analysis = {
                "intent": "information_seeking",
                "complexity": "medium",
                "topics": [],
                "entities": [],
                "sentiment": "neutral",
                "requires_context": False
            }
            
            # Detect intent
            if any(word in query_lower for word in ["how", "what", "why", "when", "where", "who"]):
                analysis["intent"] = "question"
            elif any(word in query_lower for word in ["compare", "difference", "similar"]):
                analysis["intent"] = "comparison"
            elif any(word in query_lower for word in ["summarize", "summary", "overview"]):
                analysis["intent"] = "summarization"
            elif any(word in query_lower for word in ["explain", "describe", "tell me about"]):
                analysis["intent"] = "explanation"
            
            # Detect complexity
            word_count = len(query.split())
            if word_count < 5:
                analysis["complexity"] = "simple"
            elif word_count > 15:
                analysis["complexity"] = "complex"
            
            # Extract potential topics
            important_words = [word for word in query.split() if len(word) > 3 and word.isalpha()]
            analysis["topics"] = important_words[:5]
            
            # Detect if context is needed
            if any(word in query_lower for word in ["this", "that", "it", "they", "them"]):
                analysis["requires_context"] = True
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing query intent: {str(e)}")
            return {
                "intent": "information_seeking",
                "complexity": "medium",
                "topics": [],
                "entities": [],
                "sentiment": "neutral",
                "requires_context": False
            }
    
    async def _get_relevant_documents(
        self,
        query: str,
        user_id: str,
        context_documents: Optional[List[str]] = None,
        max_sources: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get relevant documents for the query
        
        Args:
            query: User's query
            user_id: User identifier
            context_documents: Specific documents to focus on
            max_sources: Maximum number of sources
            
        Returns:
            List of relevant documents
        """
        try:
            # Get user's documents
            if context_documents:
                # Use specific documents if provided
                result = self.supabase.table("documents").select("*").in_("id", context_documents).execute()
            else:
                # Search all user documents
                result = self.supabase.table("documents").select("*").eq("user_id", user_id).execute()
            
            if not result.data:
                return []
            
            # Perform keyword matching
            query_terms = query.lower().split()
            matches = []
            
            for doc in result.data:
                score = 0
                title = doc.get('title', '').lower()
                summary = doc.get('summary', '').lower()
                tags = [tag.lower() for tag in doc.get('tags', [])]
                
                # Calculate relevance score
                for term in query_terms:
                    if term in title:
                        score += 3
                    if term in summary:
                        score += 2
                    if any(term in tag for tag in tags):
                        score += 1
                
                if score > 0:
                    matches.append({
                        'document_title': doc.get('title', ''),
                        'document_url': doc.get('source_url', ''),
                        'content': doc.get('summary', '')[:500],
                        'similarity': score / 10.0,
                        'document_id': doc.get('id'),
                        'tags': doc.get('tags', [])
                    })
            
            # Sort by score and limit
            matches.sort(key=lambda x: x['similarity'], reverse=True)
            return matches[:max_sources]
            
        except Exception as e:
            logger.error(f"Error getting relevant documents: {str(e)}")
            return []
    
    async def _generate_enhanced_response(
        self,
        query: str,
        search_results: List[Dict[str, Any]],
        conversation_history: List[Dict[str, Any]],
        response_type: str,
        query_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate enhanced response based on response type and context
        
        Args:
            query: User's query
            search_results: Relevant documents
            conversation_history: Previous conversation messages
            response_type: Type of response desired
            query_analysis: Query analysis results
            
        Returns:
            Generated response with metadata
        """
        try:
            if not search_results:
                return {
                    "response": f"I couldn't find any relevant information about '{query}' in your documents. Try rephrasing your question or adding more content to your library.",
                    "confidence": 0.0,
                    "suggestions": [
                        "Try using different keywords",
                        "Check if you have relevant documents in your library",
                        "Consider adding more content related to your query"
                    ]
                }
            
            # Prepare context
            context = self._prepare_enhanced_context(search_results, conversation_history)
            
            # Generate response based on type
            if response_type == "summary":
                response = await self._generate_summary_response(query, context, search_results)
            elif response_type == "detailed":
                response = await self._generate_detailed_response(query, context, search_results)
            elif response_type == "bullet_points":
                response = await self._generate_bullet_response(query, context, search_results)
            else:  # comprehensive
                response = await self._generate_comprehensive_response(query, context, search_results, query_analysis)
            
            # Calculate confidence
            confidence = self._calculate_enhanced_confidence(search_results, query_analysis)
            
            # Generate suggestions
            suggestions = await self._generate_enhanced_suggestions(query, search_results, query_analysis)
            
            return {
                "response": response,
                "confidence": confidence,
                "suggestions": suggestions
            }
            
        except Exception as e:
            logger.error(f"Error generating enhanced response: {str(e)}")
            return {
                "response": f"I found some relevant information about '{query}', but encountered an error while generating a response.",
                "confidence": 0.0,
                "suggestions": ["Try again", "Check your query"]
            }
    
    def _prepare_enhanced_context(
        self,
        search_results: List[Dict[str, Any]],
        conversation_history: List[Dict[str, Any]]
    ) -> str:
        """
        Prepare enhanced context including conversation history
        
        Args:
            search_results: Relevant documents
            conversation_history: Previous conversation messages
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        # Add conversation history context
        if conversation_history:
            context_parts.append("Previous conversation context:")
            for msg in conversation_history[-3:]:  # Last 3 messages
                context_parts.append(f"User: {msg.get('user_message', '')}")
                context_parts.append(f"Assistant: {msg.get('ai_response', '')[:200]}...")
            context_parts.append("---")
        
        # Add current search results
        context_parts.append("Relevant documents:")
        for i, result in enumerate(search_results, 1):
            context_parts.append(f"""
Document {i}: {result.get('document_title', 'Unknown')}
Relevance: {result.get('similarity', 0.0):.2f}
Content: {result.get('content', '')}
---""")
        
        return '\n'.join(context_parts)
    
    async def _generate_comprehensive_response(
        self,
        query: str,
        context: str,
        search_results: List[Dict[str, Any]],
        query_analysis: Dict[str, Any]
    ) -> str:
        """
        Generate comprehensive response
        
        Args:
            query: User's query
            context: Prepared context
            search_results: Relevant documents
            query_analysis: Query analysis
            
        Returns:
            Comprehensive response
        """
        prompt = f"""You are a helpful research assistant. Based on the following context, provide a comprehensive response to the user's query.

User Query: {query}
Query Intent: {query_analysis.get('intent', 'information_seeking')}
Query Complexity: {query_analysis.get('complexity', 'medium')}

Context:
{context}

Instructions:
1. Provide a comprehensive, well-structured response (3-5 paragraphs)
2. Synthesize information from multiple documents when relevant
3. Be specific and cite information from the documents
4. Address the user's intent appropriately
5. Use a helpful, informative tone
6. If the documents don't fully answer the question, acknowledge this
7. Consider the conversation context if this is a follow-up question

Response:"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text.strip()
    
    async def _generate_summary_response(
        self,
        query: str,
        context: str,
        search_results: List[Dict[str, Any]]
    ) -> str:
        """
        Generate summary response
        
        Args:
            query: User's query
            context: Prepared context
            search_results: Relevant documents
            
        Returns:
            Summary response
        """
        prompt = f"""Based on the following documents, provide a concise summary answering the user's question.

User Query: {query}

Documents:
{context}

Instructions:
1. Provide a brief, focused summary (1-2 paragraphs)
2. Highlight the most important points
3. Be concise but informative
4. Focus on directly answering the question

Summary:"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=800,
            temperature=0.2,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text.strip()
    
    async def _generate_detailed_response(
        self,
        query: str,
        context: str,
        search_results: List[Dict[str, Any]]
    ) -> str:
        """
        Generate detailed response
        
        Args:
            query: User's query
            context: Prepared context
            search_results: Relevant documents
            
        Returns:
            Detailed response
        """
        prompt = f"""Based on the following documents, provide a detailed, in-depth response to the user's question.

User Query: {query}

Documents:
{context}

Instructions:
1. Provide a detailed, thorough response (4-6 paragraphs)
2. Include specific examples and details from the documents
3. Explore different aspects and implications
4. Provide comprehensive coverage of the topic
5. Include relevant quotes or specific information
6. Consider different perspectives or approaches

Detailed Response:"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text.strip()
    
    async def _generate_bullet_response(
        self,
        query: str,
        context: str,
        search_results: List[Dict[str, Any]]
    ) -> str:
        """
        Generate bullet-point response
        
        Args:
            query: User's query
            context: Prepared context
            search_results: Relevant documents
            
        Returns:
            Bullet-point response
        """
        prompt = f"""Based on the following documents, provide a bullet-point response to the user's question.

User Query: {query}

Documents:
{context}

Instructions:
1. Provide key points in bullet format
2. Include 5-8 main points
3. Be concise but informative
4. Focus on the most important information
5. Use clear, actionable language

Bullet Points:"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            temperature=0.2,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text.strip()
    
    def _calculate_enhanced_confidence(
        self,
        search_results: List[Dict[str, Any]],
        query_analysis: Dict[str, Any]
    ) -> float:
        """
        Calculate enhanced confidence score
        
        Args:
            search_results: Relevant documents
            query_analysis: Query analysis results
            
        Returns:
            Confidence score
        """
        if not search_results:
            return 0.0
        
        # Base confidence from search results
        avg_relevance = sum(r.get('similarity', 0.0) for r in search_results) / len(search_results)
        result_factor = min(len(search_results) / 5.0, 1.0)
        top_score = search_results[0].get('similarity', 0.0) if search_results else 0.0
        
        # Adjust based on query complexity
        complexity_factor = {
            "simple": 1.0,
            "medium": 0.9,
            "complex": 0.8
        }.get(query_analysis.get("complexity", "medium"), 0.9)
        
        # Calculate final confidence
        confidence = (avg_relevance * 0.4) + (result_factor * 0.3) + (top_score * 0.2) + (complexity_factor * 0.1)
        
        return min(confidence, 1.0)
    
    async def _generate_enhanced_suggestions(
        self,
        query: str,
        search_results: List[Dict[str, Any]],
        query_analysis: Dict[str, Any]
    ) -> List[str]:
        """
        Generate enhanced follow-up suggestions
        
        Args:
            query: User's query
            search_results: Relevant documents
            query_analysis: Query analysis results
            
        Returns:
            List of suggestions
        """
        try:
            suggestions = []
            
            # Intent-based suggestions
            intent = query_analysis.get("intent", "information_seeking")
            if intent == "comparison":
                suggestions.extend([
                    "Can you provide more details about the differences?",
                    "What are the similarities between these topics?",
                    "How do these compare in terms of practical applications?"
                ])
            elif intent == "summarization":
                suggestions.extend([
                    "Can you provide a more detailed analysis?",
                    "What are the key takeaways from this information?",
                    "How can I apply this information practically?"
                ])
            elif intent == "explanation":
                suggestions.extend([
                    "Can you provide examples of this concept?",
                    "What are the implications of this information?",
                    "How does this relate to other topics?"
                ])
            else:
                # General suggestions based on topics
                topics = query_analysis.get("topics", [])
                if topics:
                    suggestions.extend([
                        f"Tell me more about {topics[0]}",
                        f"How does {topics[0]} relate to other concepts?",
                        "What are the practical applications of this information?"
                    ])
            
            # Add general suggestions
            suggestions.extend([
                "Can you provide specific examples?",
                "What are the main arguments or perspectives?",
                "How recent is this information?"
            ])
            
            return suggestions[:5]
            
        except Exception as e:
            logger.error(f"Error generating suggestions: {str(e)}")
            return [
                "Try rephrasing your question",
                "Search for related topics",
                "Check your document library for more content"
            ]
    
    async def _store_conversation_message(
        self,
        session_id: str,
        user_message: str,
        ai_response: str,
        sources: List[Dict[str, Any]],
        confidence: float
    ):
        """
        Store conversation message in database
        
        Args:
            session_id: Session ID
            user_message: User's message
            ai_response: AI's response
            sources: Sources used
            confidence: Response confidence
        """
        try:
            message_data = {
                "message_id": str(uuid.uuid4()),
                "session_id": session_id,
                "user_message": user_message,
                "ai_response": ai_response,
                "timestamp": datetime.utcnow().isoformat(),
                "sources_used": sources,
                "confidence": confidence,
                "query_intent": "information_seeking"  # Could be enhanced with intent detection
            }
            
            self.supabase.table("conversation_messages").insert(message_data).execute()
            
            # Update session message count
            self.supabase.table("conversation_sessions").update({
                "message_count": self.supabase.rpc("increment", {"table": "conversation_sessions", "column": "message_count", "id": session_id}).execute()
            }).eq("session_id", session_id).execute()
            
        except Exception as e:
            logger.error(f"Error storing conversation message: {str(e)}")
    
    async def _update_session_context(
        self,
        session_id: str,
        search_results: List[Dict[str, Any]]
    ):
        """
        Update session with new context documents
        
        Args:
            session_id: Session ID
            search_results: Search results
        """
        try:
            # Extract document IDs from search results
            doc_ids = [result.get("document_id") for result in search_results if result.get("document_id")]
            
            if doc_ids:
                # Update session context documents
                self.supabase.table("conversation_sessions").update({
                    "context_documents": doc_ids
                }).eq("session_id", session_id).execute()
                
        except Exception as e:
            logger.error(f"Error updating session context: {str(e)}")
    
    async def get_conversation_summary(self, session_id: str) -> str:
        """
        Generate a summary of the conversation
        
        Args:
            session_id: Session ID
            
        Returns:
            Conversation summary
        """
        try:
            # Get conversation messages
            messages = await self.get_conversation_history(session_id)
            
            if not messages:
                return "No conversation history found."
            
            # Prepare conversation text
            conversation_text = ""
            for msg in messages:
                conversation_text += f"User: {msg.get('user_message', '')}\n"
                conversation_text += f"Assistant: {msg.get('ai_response', '')}\n\n"
            
            # Generate summary
            prompt = f"""Please provide a brief summary of this conversation:

{conversation_text}

Summary (2-3 sentences):"""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=200,
                temperature=0.2,
                messages=[{"role": "user", "content": prompt}]
            )
            
            summary = response.content[0].text.strip()
            
            # Update session with summary
            self.supabase.table("conversation_sessions").update({
                "conversation_summary": summary
            }).eq("session_id", session_id).execute()
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating conversation summary: {str(e)}")
            return "Unable to generate conversation summary."
