"""
Enhanced Search Service
Multi-modal search, advanced filtering, and improved result ranking
"""

import asyncio
import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import logging
from datetime import datetime, timedelta
import re

from core.config import get_settings
from services.content_processor import ContentProcessor
from database.client import get_supabase_service_client

logger = logging.getLogger(__name__)

class SearchType(Enum):
    """Search type enumeration"""
    SEMANTIC = "semantic"
    KEYWORD = "keyword"
    HYBRID = "hybrid"
    TAG = "tag"
    CONTENT_TYPE = "content_type"
    QUALITY = "quality"
    DATE_RANGE = "date_range"

class FilterType(Enum):
    """Filter type enumeration"""
    CONTENT_TYPE = "content_type"
    QUALITY = "quality"
    LANGUAGE = "language"
    DATE_RANGE = "date_range"
    WORD_COUNT = "word_count"
    READING_TIME = "reading_time"
    COMPLEXITY = "complexity"
    TAGS = "tags"

class SortType(Enum):
    """Sort type enumeration"""
    RELEVANCE = "relevance"
    DATE_NEWEST = "date_newest"
    DATE_OLDEST = "date_oldest"
    QUALITY = "quality"
    READING_TIME = "reading_time"
    COMPLEXITY = "complexity"
    WORD_COUNT = "word_count"

class EnhancedSearchService:
    """Enhanced search service with multi-modal capabilities"""
    
    def __init__(self):
        self.settings = get_settings()
        self.content_processor = ContentProcessor()
        self.supabase = get_supabase_service_client()
        
    async def search(self, query: str, user_id: str, search_type: SearchType = SearchType.HYBRID,
                    filters: Dict[str, Any] = None, sort_by: SortType = SortType.RELEVANCE,
                    limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """Enhanced search with multiple search types and filtering"""
        try:
            # Initialize filters
            if filters is None:
                filters = {}
                
            # Build base query
            base_query = self.supabase.table("documents").select("*").eq("user_id", user_id)
            
            # Apply filters
            base_query = self._apply_filters(base_query, filters)
            
            # Perform search based on type
            if search_type == SearchType.SEMANTIC:
                results = await self._semantic_search(query, base_query, limit, offset)
            elif search_type == SearchType.KEYWORD:
                results = await self._keyword_search(query, base_query, limit, offset)
            elif search_type == SearchType.TAG:
                results = await self._tag_search(query, base_query, limit, offset)
            elif search_type == SearchType.CONTENT_TYPE:
                results = await self._content_type_search(query, base_query, limit, offset)
            elif search_type == SearchType.QUALITY:
                results = await self._quality_search(query, base_query, limit, offset)
            elif search_type == SearchType.DATE_RANGE:
                results = await self._date_range_search(query, base_query, limit, offset)
            else:  # HYBRID
                results = await self._hybrid_search(query, base_query, limit, offset)
                
            # Sort results
            results = self._sort_results(results, sort_by)
            
            # Add search metadata
            search_metadata = {
                "query": query,
                "search_type": search_type.value,
                "filters_applied": filters,
                "sort_by": sort_by.value,
                "total_results": len(results),
                "limit": limit,
                "offset": offset,
                "search_timestamp": datetime.utcnow().isoformat()
            }
            
            return {
                "results": results,
                "metadata": search_metadata
            }
            
        except Exception as e:
            logger.error(f"Enhanced search failed: {str(e)}")
            raise Exception(f"Search failed: {str(e)}")
            
    async def _semantic_search(self, query: str, base_query, limit: int, offset: int) -> List[Dict[str, Any]]:
        """Semantic search using embeddings"""
        try:
            # Generate query embedding
            query_embedding = await self.content_processor._generate_embedding(query)
            
            # Search in document chunks
            chunks_result = self.supabase.rpc(
                'match_document_chunks',
                {
                    'query_embedding': query_embedding,
                    'match_threshold': 0.7,
                    'match_count': limit * 3  # Get more chunks for better ranking
                }
            ).execute()
            
            if not chunks_result.data:
                return []
                
            # Get unique document IDs from chunks
            document_ids = list(set([chunk['document_id'] for chunk in chunks_result.data]))
            
            # Get full documents
            documents_result = base_query.in_('id', document_ids).execute()
            
            if not documents_result.data:
                return []
                
            # Calculate relevance scores
            scored_documents = []
            for doc in documents_result.data:
                # Find chunks for this document
                doc_chunks = [c for c in chunks_result.data if c['document_id'] == doc['id']]
                
                # Calculate average similarity score
                if doc_chunks:
                    avg_score = sum(chunk.get('similarity', 0) for chunk in doc_chunks) / len(doc_chunks)
                    doc['relevance_score'] = avg_score
                    doc['matching_chunks'] = len(doc_chunks)
                else:
                    doc['relevance_score'] = 0.0
                    doc['matching_chunks'] = 0
                    
                scored_documents.append(doc)
                
            # Sort by relevance score
            scored_documents.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            return scored_documents[:limit]
            
        except Exception as e:
            logger.error(f"Semantic search failed: {str(e)}")
            return []
            
    async def _keyword_search(self, query: str, base_query, limit: int, offset: int) -> List[Dict[str, Any]]:
        """Keyword-based search using full-text search"""
        try:
            # Split query into keywords
            keywords = self._extract_keywords(query)
            
            # Build keyword search query
            search_query = base_query
            
            # Search in title, summary, and content
            for keyword in keywords:
                search_query = search_query.or_(
                    f"title.ilike.%{keyword}%,summary.ilike.%{keyword}%"
                )
                
            # Execute search
            result = search_query.limit(limit).offset(offset).execute()
            
            if not result.data:
                return []
                
            # Calculate keyword relevance scores
            for doc in result.data:
                doc['relevance_score'] = self._calculate_keyword_score(doc, keywords)
                
            # Sort by keyword relevance
            result.data.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            return result.data
            
        except Exception as e:
            logger.error(f"Keyword search failed: {str(e)}")
            return []
            
    async def _tag_search(self, query: str, base_query, limit: int, offset: int) -> List[Dict[str, Any]]:
        """Search by tags"""
        try:
            # Extract tags from query
            tags = self._extract_tags(query)
            
            if not tags:
                return []
                
            # Search for documents with matching tags
            search_query = base_query
            
            for tag in tags:
                search_query = search_query.contains('tags', [tag])
                
            result = search_query.limit(limit).offset(offset).execute()
            
            if not result.data:
                return []
                
            # Calculate tag relevance scores
            for doc in result.data:
                doc['relevance_score'] = self._calculate_tag_score(doc, tags)
                
            # Sort by tag relevance
            result.data.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            return result.data
            
        except Exception as e:
            logger.error(f"Tag search failed: {str(e)}")
            return []
            
    async def _content_type_search(self, query: str, base_query, limit: int, offset: int) -> List[Dict[str, Any]]:
        """Search by content type"""
        try:
            # Map query to content type
            content_type = self._map_query_to_content_type(query)
            
            if not content_type:
                return []
                
            # Search for documents with matching content type
            result = base_query.eq('content_type', content_type).limit(limit).offset(offset).execute()
            
            if not result.data:
                return []
                
            # Calculate content type relevance
            for doc in result.data:
                doc['relevance_score'] = 1.0  # Perfect match for content type
                
            return result.data
            
        except Exception as e:
            logger.error(f"Content type search failed: {str(e)}")
            return []
            
    async def _quality_search(self, query: str, base_query, limit: int, offset: int) -> List[Dict[str, Any]]:
        """Search by quality level"""
        try:
            # Map query to quality level
            quality = self._map_query_to_quality(query)
            
            if not quality:
                return []
                
            # Search for documents with matching quality
            result = base_query.eq('quality', quality).limit(limit).offset(offset).execute()
            
            if not result.data:
                return []
                
            # Calculate quality relevance
            for doc in result.data:
                doc['relevance_score'] = 1.0  # Perfect match for quality
                
            return result.data
            
        except Exception as e:
            logger.error(f"Quality search failed: {str(e)}")
            return []
            
    async def _date_range_search(self, query: str, base_query, limit: int, offset: int) -> List[Dict[str, Any]]:
        """Search by date range"""
        try:
            # Parse date range from query
            date_range = self._parse_date_range(query)
            
            if not date_range:
                return []
                
            start_date, end_date = date_range
            
            # Search for documents within date range
            result = base_query.gte('created_at', start_date.isoformat()).lte('created_at', end_date.isoformat()).limit(limit).offset(offset).execute()
            
            if not result.data:
                return []
                
            # Calculate date relevance (newer documents get higher scores)
            for doc in result.data:
                created_at = datetime.fromisoformat(doc['created_at'].replace('Z', '+00:00'))
                days_old = (datetime.now(created_at.tzinfo) - created_at).days
                doc['relevance_score'] = max(0.1, 1.0 - (days_old / 365))  # Decay over time
                
            # Sort by date relevance
            result.data.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            return result.data
            
        except Exception as e:
            logger.error(f"Date range search failed: {str(e)}")
            return []
            
    async def _hybrid_search(self, query: str, base_query, limit: int, offset: int) -> List[Dict[str, Any]]:
        """Hybrid search combining multiple search types"""
        try:
            # Perform multiple searches in parallel
            search_tasks = [
                self._semantic_search(query, base_query, limit * 2, 0),
                self._keyword_search(query, base_query, limit * 2, 0),
                self._tag_search(query, base_query, limit * 2, 0)
            ]
            
            results = await asyncio.gather(*search_tasks, return_exceptions=True)
            
            # Combine and deduplicate results
            all_documents = {}
            
            for i, result in enumerate(results):
                if isinstance(result, list):
                    for doc in result:
                        doc_id = doc['id']
                        if doc_id not in all_documents:
                            all_documents[doc_id] = doc
                        else:
                            # Combine relevance scores
                            existing_score = all_documents[doc_id]['relevance_score']
                            new_score = doc['relevance_score']
                            # Weight semantic search higher
                            if i == 0:  # Semantic search
                                all_documents[doc_id]['relevance_score'] = (existing_score * 0.3 + new_score * 0.7)
                            else:
                                all_documents[doc_id]['relevance_score'] = (existing_score * 0.6 + new_score * 0.4)
                                
            # Convert to list and sort by combined relevance
            combined_results = list(all_documents.values())
            combined_results.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            return combined_results[:limit]
            
        except Exception as e:
            logger.error(f"Hybrid search failed: {str(e)}")
            return []
            
    def _apply_filters(self, query, filters: Dict[str, Any]):
        """Apply filters to the base query"""
        try:
            for filter_type, filter_value in filters.items():
                if filter_type == FilterType.CONTENT_TYPE.value and filter_value:
                    query = query.eq('content_type', filter_value)
                elif filter_type == FilterType.QUALITY.value and filter_value:
                    query = query.eq('quality', filter_value)
                elif filter_type == FilterType.LANGUAGE.value and filter_value:
                    query = query.eq('language', filter_value)
                elif filter_type == FilterType.WORD_COUNT.value and filter_value:
                    min_words, max_words = filter_value
                    if min_words:
                        query = query.gte('word_count', min_words)
                    if max_words:
                        query = query.lte('word_count', max_words)
                elif filter_type == FilterType.READING_TIME.value and filter_value:
                    min_time, max_time = filter_value
                    if min_time:
                        query = query.gte('reading_time_minutes', min_time)
                    if max_time:
                        query = query.lte('reading_time_minutes', max_time)
                elif filter_type == FilterType.COMPLEXITY.value and filter_value:
                    min_complexity, max_complexity = filter_value
                    if min_complexity:
                        query = query.gte('complexity_score', min_complexity)
                    if max_complexity:
                        query = query.lte('complexity_score', max_complexity)
                elif filter_type == FilterType.TAGS.value and filter_value:
                    for tag in filter_value:
                        query = query.contains('tags', [tag])
                elif filter_type == FilterType.DATE_RANGE.value and filter_value:
                    start_date, end_date = filter_value
                    if start_date:
                        query = query.gte('created_at', start_date.isoformat())
                    if end_date:
                        query = query.lte('created_at', end_date.isoformat())
                        
            return query
            
        except Exception as e:
            logger.error(f"Filter application failed: {str(e)}")
            return query
            
    def _sort_results(self, results: List[Dict[str, Any]], sort_by: SortType) -> List[Dict[str, Any]]:
        """Sort results based on sort type"""
        try:
            if sort_by == SortType.RELEVANCE:
                # Already sorted by relevance score
                pass
            elif sort_by == SortType.DATE_NEWEST:
                results.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            elif sort_by == SortType.DATE_OLDEST:
                results.sort(key=lambda x: x.get('created_at', ''))
            elif sort_by == SortType.QUALITY:
                quality_order = {'excellent': 4, 'good': 3, 'fair': 2, 'poor': 1}
                results.sort(key=lambda x: quality_order.get(x.get('quality', 'fair'), 2), reverse=True)
            elif sort_by == SortType.READING_TIME:
                results.sort(key=lambda x: x.get('reading_time_minutes', 0), reverse=True)
            elif sort_by == SortType.COMPLEXITY:
                results.sort(key=lambda x: x.get('complexity_score', 0.5), reverse=True)
            elif sort_by == SortType.WORD_COUNT:
                results.sort(key=lambda x: x.get('word_count', 0), reverse=True)
                
            return results
            
        except Exception as e:
            logger.error(f"Result sorting failed: {str(e)}")
            return results
            
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract keywords from query"""
        try:
            # Simple keyword extraction
            keywords = re.findall(r'\b\w+\b', query.lower())
            # Remove common stop words
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
            keywords = [kw for kw in keywords if kw not in stop_words and len(kw) > 2]
            return keywords[:10]  # Limit to 10 keywords
            
        except Exception as e:
            logger.error(f"Keyword extraction failed: {str(e)}")
            return []
            
    def _extract_tags(self, query: str) -> List[str]:
        """Extract tags from query"""
        try:
            # Look for tag-like patterns
            tags = re.findall(r'#(\w+)', query)
            # Also look for quoted terms that might be tags
            quoted_tags = re.findall(r'"([^"]+)"', query)
            tags.extend(quoted_tags)
            return tags
            
        except Exception as e:
            logger.error(f"Tag extraction failed: {str(e)}")
            return []
            
    def _map_query_to_content_type(self, query: str) -> Optional[str]:
        """Map query to content type"""
        try:
            query_lower = query.lower()
            
            if any(word in query_lower for word in ['technical', 'api', 'code', 'programming', 'development']):
                return 'technical'
            elif any(word in query_lower for word in ['academic', 'research', 'study', 'paper', 'thesis']):
                return 'academic'
            elif any(word in query_lower for word in ['news', 'article', 'report', 'announcement']):
                return 'news'
            elif any(word in query_lower for word in ['blog', 'post', 'opinion', 'thoughts']):
                return 'blog_post'
            elif any(word in query_lower for word in ['documentation', 'guide', 'manual', 'tutorial']):
                return 'documentation'
            else:
                return None
                
        except Exception as e:
            logger.error(f"Content type mapping failed: {str(e)}")
            return None
            
    def _map_query_to_quality(self, query: str) -> Optional[str]:
        """Map query to quality level"""
        try:
            query_lower = query.lower()
            
            if any(word in query_lower for word in ['excellent', 'high quality', 'best', 'top']):
                return 'excellent'
            elif any(word in query_lower for word in ['good', 'quality', 'well written']):
                return 'good'
            elif any(word in query_lower for word in ['fair', 'average', 'okay']):
                return 'fair'
            elif any(word in query_lower for word in ['poor', 'low quality', 'bad']):
                return 'poor'
            else:
                return None
                
        except Exception as e:
            logger.error(f"Quality mapping failed: {str(e)}")
            return None
            
    def _parse_date_range(self, query: str) -> Optional[Tuple[datetime, datetime]]:
        """Parse date range from query"""
        try:
            query_lower = query.lower()
            
            # Look for date patterns
            if 'today' in query_lower:
                today = datetime.now()
                return (today.replace(hour=0, minute=0, second=0, microsecond=0), today)
            elif 'yesterday' in query_lower:
                yesterday = datetime.now() - timedelta(days=1)
                return (yesterday.replace(hour=0, minute=0, second=0, microsecond=0), yesterday)
            elif 'this week' in query_lower:
                today = datetime.now()
                start_of_week = today - timedelta(days=today.weekday())
                return (start_of_week.replace(hour=0, minute=0, second=0, microsecond=0), today)
            elif 'this month' in query_lower:
                today = datetime.now()
                start_of_month = today.replace(day=1)
                return (start_of_month.replace(hour=0, minute=0, second=0, microsecond=0), today)
            elif 'last week' in query_lower:
                today = datetime.now()
                start_of_last_week = today - timedelta(days=today.weekday() + 7)
                end_of_last_week = start_of_last_week + timedelta(days=6)
                return (start_of_last_week.replace(hour=0, minute=0, second=0, microsecond=0), end_of_last_week)
            elif 'last month' in query_lower:
                today = datetime.now()
                if today.month == 1:
                    last_month = today.replace(year=today.year - 1, month=12)
                else:
                    last_month = today.replace(month=today.month - 1)
                start_of_last_month = last_month.replace(day=1)
                return (start_of_last_month.replace(hour=0, minute=0, second=0, microsecond=0), today)
            else:
                return None
                
        except Exception as e:
            logger.error(f"Date range parsing failed: {str(e)}")
            return None
            
    def _calculate_keyword_score(self, doc: Dict[str, Any], keywords: List[str]) -> float:
        """Calculate keyword relevance score"""
        try:
            score = 0.0
            text = f"{doc.get('title', '')} {doc.get('summary', '')}".lower()
            
            for keyword in keywords:
                if keyword in text:
                    # Weight title matches higher
                    if keyword in doc.get('title', '').lower():
                        score += 2.0
                    else:
                        score += 1.0
                        
            return score / len(keywords) if keywords else 0.0
            
        except Exception as e:
            logger.error(f"Keyword score calculation failed: {str(e)}")
            return 0.0
            
    def _calculate_tag_score(self, doc: Dict[str, Any], tags: List[str]) -> float:
        """Calculate tag relevance score"""
        try:
            score = 0.0
            doc_tags = doc.get('tags', [])
            
            for tag in tags:
                if tag in doc_tags:
                    score += 1.0
                    
            return score / len(tags) if tags else 0.0
            
        except Exception as e:
            logger.error(f"Tag score calculation failed: {str(e)}")
            return 0.0
