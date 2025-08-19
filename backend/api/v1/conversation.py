"""
Enhanced Conversational API endpoints
Handles multi-turn conversations, session management, and advanced conversational features
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
import uuid
from datetime import datetime

from core.config import get_settings
from auth.middleware import get_current_user
from models.schemas import (
    ConversationalQuery, 
    ConversationalResponse, 
    ConversationSession,
    ConversationMessage
)
from services.enhanced_conversational import EnhancedConversationalService
from database.client import get_supabase_service_client

router = APIRouter(prefix="/conversation", tags=["Enhanced Conversation"])

@router.post("/start", response_model=ConversationSession)
async def start_conversation(
    current_user: dict = Depends(get_current_user)
):
    """
    Start a new conversation session
    """
    try:
        service = EnhancedConversationalService()
        result = await service.start_conversation(current_user.get('id'))
        
        if result.get('status') == 'error':
            raise HTTPException(status_code=500, detail=result.get('message'))
        
        # Get the created session
        supabase = get_supabase_service_client()
        session_result = supabase.table("conversation_sessions").select("*").eq("session_id", result['session_id']).single().execute()
        
        return ConversationSession(**session_result.data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start conversation: {str(e)}")

@router.post("/query", response_model=ConversationalResponse)
async def enhanced_conversational_query(
    query: ConversationalQuery,
    current_user: dict = Depends(get_current_user)
):
    """
    Process an enhanced conversational query with multi-turn support
    """
    try:
        service = EnhancedConversationalService()
        
        response = await service.process_conversational_query(
            query=query.query,
            user_id=current_user.get('id'),
            conversation_id=query.conversation_id,
            context_documents=query.context_documents,
            response_type=query.response_type,
            include_sources=query.include_sources,
            max_sources=query.max_sources
        )
        
        return ConversationalResponse(**response)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversational query failed: {str(e)}")

@router.get("/sessions", response_model=List[ConversationSession])
async def get_user_conversations(
    current_user: dict = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0)
):
    """
    Get user's conversation sessions
    """
    try:
        supabase = get_supabase_service_client()
        result = supabase.table("conversation_sessions").select("*").eq("user_id", current_user.get('id')).order("last_activity", desc=True).range(offset, offset + limit - 1).execute()
        
        return [ConversationSession(**session) for session in result.data]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get conversations: {str(e)}")

@router.get("/sessions/{session_id}", response_model=ConversationSession)
async def get_conversation_session(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get specific conversation session
    """
    try:
        supabase = get_supabase_service_client()
        result = supabase.table("conversation_sessions").select("*").eq("session_id", session_id).eq("user_id", current_user.get('id')).single().execute()
        
        return ConversationSession(**result.data)
        
    except Exception as e:
        raise HTTPException(status_code=404, detail="Conversation session not found")

@router.get("/sessions/{session_id}/messages", response_model=List[ConversationMessage])
async def get_conversation_messages(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Get messages from a conversation session
    """
    try:
        # Verify session belongs to user
        supabase = get_supabase_service_client()
        session_result = supabase.table("conversation_sessions").select("session_id").eq("session_id", session_id).eq("user_id", current_user.get('id')).single().execute()
        
        if not session_result.data:
            raise HTTPException(status_code=404, detail="Conversation session not found")
        
        # Get messages
        result = supabase.table("conversation_messages").select("*").eq("session_id", session_id).order("timestamp", desc=False).range(offset, offset + limit - 1).execute()
        
        return [ConversationMessage(**message) for message in result.data]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get messages: {str(e)}")

@router.get("/sessions/{session_id}/summary")
async def get_conversation_summary(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get or generate a summary of a conversation session
    """
    try:
        # Verify session belongs to user
        supabase = get_supabase_service_client()
        session_result = supabase.table("conversation_sessions").select("session_id, conversation_summary").eq("session_id", session_id).eq("user_id", current_user.get('id')).single().execute()
        
        if not session_result.data:
            raise HTTPException(status_code=404, detail="Conversation session not found")
        
        # If summary exists, return it
        if session_result.data.get('conversation_summary'):
            return {"summary": session_result.data['conversation_summary']}
        
        # Generate new summary
        service = EnhancedConversationalService()
        summary = await service.get_conversation_summary(session_id)
        
        return {"summary": summary}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get conversation summary: {str(e)}")

@router.delete("/sessions/{session_id}")
async def delete_conversation_session(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a conversation session and all its messages
    """
    try:
        supabase = get_supabase_service_client()
        
        # Verify session belongs to user
        session_result = supabase.table("conversation_sessions").select("session_id").eq("session_id", session_id).eq("user_id", current_user.get('id')).single().execute()
        
        if not session_result.data:
            raise HTTPException(status_code=404, detail="Conversation session not found")
        
        # Delete session (messages will be deleted via CASCADE)
        supabase.table("conversation_sessions").delete().eq("session_id", session_id).execute()
        
        return {"message": "Conversation session deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete conversation: {str(e)}")

@router.get("/analytics")
async def get_conversation_analytics(
    current_user: dict = Depends(get_current_user),
    days: int = Query(7, ge=1, le=30)
):
    """
    Get conversation analytics for the user
    """
    try:
        supabase = get_supabase_service_client()
        
        # Get analytics from the view
        result = supabase.table("conversation_analytics").select("*").eq("user_id", current_user.get('id')).gte("created_at", datetime.utcnow().isoformat()).execute()
        
        if not result.data:
            return {
                "total_sessions": 0,
                "total_messages": 0,
                "avg_confidence": 0.0,
                "avg_session_duration": 0,
                "recent_activity": []
            }
        
        # Calculate analytics
        total_sessions = len(result.data)
        total_messages = sum(session.get('total_messages', 0) for session in result.data)
        avg_confidence = sum(session.get('avg_confidence', 0) for session in result.data) / total_sessions if total_sessions > 0 else 0
        avg_duration = sum(session.get('conversation_duration_seconds', 0) for session in result.data) / total_sessions if total_sessions > 0 else 0
        
        # Get recent activity
        recent_sessions = sorted(result.data, key=lambda x: x.get('last_activity', ''), reverse=True)[:5]
        
        return {
            "total_sessions": total_sessions,
            "total_messages": total_messages,
            "avg_confidence": round(avg_confidence, 2),
            "avg_session_duration": round(avg_duration, 2),
            "recent_activity": [
                {
                    "session_id": session.get('session_id'),
                    "message_count": session.get('message_count', 0),
                    "last_activity": session.get('last_activity'),
                    "summary": session.get('conversation_summary', '')[:100] + '...' if session.get('conversation_summary') else ''
                }
                for session in recent_sessions
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

@router.post("/sessions/{session_id}/continue")
async def continue_conversation(
    session_id: str,
    query: ConversationalQuery,
    current_user: dict = Depends(get_current_user)
):
    """
    Continue an existing conversation session
    """
    try:
        # Verify session belongs to user
        supabase = get_supabase_service_client()
        session_result = supabase.table("conversation_sessions").select("session_id").eq("session_id", session_id).eq("user_id", current_user.get('id')).single().execute()
        
        if not session_result.data:
            raise HTTPException(status_code=404, detail="Conversation session not found")
        
        # Process query with existing session
        service = EnhancedConversationalService()
        response = await service.process_conversational_query(
            query=query.query,
            user_id=current_user.get('id'),
            conversation_id=session_id,
            context_documents=query.context_documents,
            response_type=query.response_type,
            include_sources=query.include_sources,
            max_sources=query.max_sources
        )
        
        return ConversationalResponse(**response)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to continue conversation: {str(e)}")

@router.get("/suggestions")
async def get_conversation_suggestions(
    current_user: dict = Depends(get_current_user),
    topic: Optional[str] = Query(None, description="Topic to get suggestions for")
):
    """
    Get conversation starter suggestions
    """
    try:
        suggestions = [
            "What are the key insights from my documents?",
            "Can you summarize the main themes in my research?",
            "What are the most important findings?",
            "How do the different documents relate to each other?",
            "What are the practical applications of this information?",
            "Can you compare different perspectives on this topic?",
            "What are the main arguments or viewpoints?",
            "How recent is this information and is it still relevant?",
            "What are the gaps or limitations in this research?",
            "What are the next steps or recommendations?"
        ]
        
        if topic:
            # Filter suggestions based on topic
            topic_suggestions = [
                f"What are the key insights about {topic}?",
                f"Can you summarize the main points about {topic}?",
                f"How does {topic} relate to other concepts?",
                f"What are the practical applications of {topic}?",
                f"What are the different perspectives on {topic}?"
            ]
            suggestions = topic_suggestions + suggestions[:5]
        
        return {"suggestions": suggestions[:10]}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get suggestions: {str(e)}")
