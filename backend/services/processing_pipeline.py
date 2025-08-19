"""
Enhanced Processing Pipeline Service
Background task optimization, status tracking, and error handling
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
import logging
from datetime import datetime, timedelta
import uuid

from core.config import get_settings
from services.content_processor import ContentProcessor
from services.ai_processor import EnhancedAIProcessor
from services.text_processor import AdvancedTextProcessor
from database.client import get_supabase_service_client

logger = logging.getLogger(__name__)

class ProcessingStatus(Enum):
    """Processing status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ProcessingStage(Enum):
    """Processing stage enumeration"""
    INITIALIZED = "initialized"
    CONTENT_EXTRACTION = "content_extraction"
    TEXT_PROCESSING = "text_processing"
    AI_ANALYSIS = "ai_analysis"
    EMBEDDING_GENERATION = "embedding_generation"
    DATABASE_STORAGE = "database_storage"
    COMPLETED = "completed"

class ProcessingTask:
    """Represents a processing task with status tracking"""
    
    def __init__(self, task_id: str, url: str, user_id: str):
        self.task_id = task_id
        self.url = url
        self.user_id = user_id
        self.status = ProcessingStatus.PENDING
        self.stage = ProcessingStage.INITIALIZED
        self.progress = 0.0
        self.start_time = None
        self.end_time = None
        self.error_message = None
        self.result = None
        self.retry_count = 0
        self.max_retries = 3
        
    def update_status(self, status: ProcessingStatus, stage: ProcessingStage = None, 
                     progress: float = None, error_message: str = None):
        """Update task status and progress"""
        self.status = status
        if stage:
            self.stage = stage
        if progress is not None:
            self.progress = progress
        if error_message:
            self.error_message = error_message
            
        if status == ProcessingStatus.PROCESSING and not self.start_time:
            self.start_time = datetime.utcnow()
        elif status in [ProcessingStatus.COMPLETED, ProcessingStatus.FAILED]:
            self.end_time = datetime.utcnow()

class EnhancedProcessingPipeline:
    """Enhanced processing pipeline with optimization and monitoring"""
    
    def __init__(self):
        self.settings = get_settings()
        self.content_processor = ContentProcessor()
        self.ai_processor = EnhancedAIProcessor()
        self.text_processor = AdvancedTextProcessor()
        self.supabase = get_supabase_service_client()
        
        # Task tracking
        self.active_tasks: Dict[str, ProcessingTask] = {}
        self.completed_tasks: Dict[str, ProcessingTask] = {}
        self.failed_tasks: Dict[str, ProcessingTask] = {}
        
        # Performance metrics
        self.metrics = {
            "total_processed": 0,
            "successful": 0,
            "failed": 0,
            "average_processing_time": 0.0,
            "total_processing_time": 0.0
        }
        
    async def process_url(self, url: str, user_id: str) -> str:
        """Start processing a URL and return task ID"""
        try:
            # Generate task ID
            task_id = str(uuid.uuid4())
            
            # Create processing task
            task = ProcessingTask(task_id, url, user_id)
            self.active_tasks[task_id] = task
            
            # Update database with initial status
            await self._update_database_status(task)
            
            # Start background processing
            asyncio.create_task(self._process_task(task))
            
            logger.info(f"Started processing task {task_id} for URL: {url}")
            return task_id
            
        except Exception as e:
            logger.error(f"Failed to start processing for URL {url}: {str(e)}")
            raise Exception(f"Failed to start processing: {str(e)}")
            
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get current status of a processing task"""
        try:
            # Check active tasks
            if task_id in self.active_tasks:
                task = self.active_tasks[task_id]
                return self._task_to_dict(task)
                
            # Check completed tasks
            if task_id in self.completed_tasks:
                task = self.completed_tasks[task_id]
                return self._task_to_dict(task)
                
            # Check failed tasks
            if task_id in self.failed_tasks:
                task = self.failed_tasks[task_id]
                return self._task_to_dict(task)
                
            # Check database
            return await self._get_database_task_status(task_id)
            
        except Exception as e:
            logger.error(f"Failed to get task status for {task_id}: {str(e)}")
            return {"error": str(e)}
            
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a processing task"""
        try:
            if task_id in self.active_tasks:
                task = self.active_tasks[task_id]
                task.update_status(ProcessingStatus.CANCELLED)
                
                # Move to completed tasks
                del self.active_tasks[task_id]
                self.completed_tasks[task_id] = task
                
                # Update database
                await self._update_database_status(task)
                
                logger.info(f"Cancelled task {task_id}")
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Failed to cancel task {task_id}: {str(e)}")
            return False
            
    async def get_processing_metrics(self) -> Dict[str, Any]:
        """Get processing pipeline metrics"""
        try:
            # Calculate additional metrics
            total_time = self.metrics["total_processing_time"]
            total_processed = self.metrics["total_processed"]
            
            if total_processed > 0:
                self.metrics["average_processing_time"] = total_time / total_processed
                self.metrics["success_rate"] = self.metrics["successful"] / total_processed
            else:
                self.metrics["average_processing_time"] = 0.0
                self.metrics["success_rate"] = 0.0
                
            return self.metrics.copy()
            
        except Exception as e:
            logger.error(f"Failed to get processing metrics: {str(e)}")
            return {"error": str(e)}
            
    async def _process_task(self, task: ProcessingTask):
        """Process a task with comprehensive error handling and retries"""
        try:
            logger.info(f"Starting processing for task {task.task_id}")
            
            # Stage 1: Content Extraction
            await self._update_task_progress(task, ProcessingStage.CONTENT_EXTRACTION, 0.1)
            content = await self._extract_content_with_retry(task)
            
            # Stage 2: Text Processing
            await self._update_task_progress(task, ProcessingStage.TEXT_PROCESSING, 0.3)
            text_analysis = await self._process_text_with_retry(task, content)
            
            # Stage 3: AI Analysis
            await self._update_task_progress(task, ProcessingStage.AI_ANALYSIS, 0.6)
            ai_results = await self._analyze_with_ai_with_retry(task, content, text_analysis)
            
            # Stage 4: Embedding Generation
            await self._update_task_progress(task, ProcessingStage.EMBEDDING_GENERATION, 0.8)
            embeddings = await self._generate_embeddings_with_retry(task, content)
            
            # Stage 5: Database Storage
            await self._update_task_progress(task, ProcessingStage.DATABASE_STORAGE, 0.9)
            await self._store_results_with_retry(task, content, text_analysis, ai_results, embeddings)
            
            # Complete task
            await self._complete_task(task, content, text_analysis, ai_results, embeddings)
            
        except Exception as e:
            await self._handle_task_error(task, str(e))
            
    async def _extract_content_with_retry(self, task: ProcessingTask) -> str:
        """Extract content with retry logic"""
        for attempt in range(task.max_retries + 1):
            try:
                logger.info(f"Extracting content for task {task.task_id} (attempt {attempt + 1})")
                content = await self.content_processor._fetch_url_content(task.url)
                
                if not content or len(content.strip()) < 50:
                    raise Exception("Insufficient content extracted")
                    
                return content
                
            except Exception as e:
                if attempt == task.max_retries:
                    raise Exception(f"Failed to extract content after {task.max_retries + 1} attempts: {str(e)}")
                    
                logger.warning(f"Content extraction failed for task {task.task_id}, attempt {attempt + 1}: {str(e)}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                
    async def _process_text_with_retry(self, task: ProcessingTask, content: str) -> Dict[str, Any]:
        """Process text with retry logic"""
        for attempt in range(task.max_retries + 1):
            try:
                logger.info(f"Processing text for task {task.task_id} (attempt {attempt + 1})")
                
                # Perform text analysis
                text_analysis = await self.text_processor.process_text(content, task.url)
                
                # Create enhanced chunks
                enhanced_chunks = self.text_processor.create_enhanced_chunks(content)
                
                return {
                    "analysis": text_analysis,
                    "chunks": enhanced_chunks
                }
                
            except Exception as e:
                if attempt == task.max_retries:
                    raise Exception(f"Failed to process text after {task.max_retries + 1} attempts: {str(e)}")
                    
                logger.warning(f"Text processing failed for task {task.task_id}, attempt {attempt + 1}: {str(e)}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                
    async def _analyze_with_ai_with_retry(self, task: ProcessingTask, content: str, 
                                        text_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze content with AI using retry logic"""
        for attempt in range(task.max_retries + 1):
            try:
                logger.info(f"Analyzing with AI for task {task.task_id} (attempt {attempt + 1})")
                
                # Get analysis parameters from text processing
                analysis = text_analysis["analysis"]
                
                # Perform AI analysis
                ai_results = await self.ai_processor.process_content(
                    content,
                    analysis.content_type.value,
                    analysis.quality.value,
                    analysis.language,
                    analysis.word_count
                )
                
                return ai_results
                
            except Exception as e:
                if attempt == task.max_retries:
                    raise Exception(f"Failed to analyze with AI after {task.max_retries + 1} attempts: {str(e)}")
                    
                logger.warning(f"AI analysis failed for task {task.task_id}, attempt {attempt + 1}: {str(e)}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                
    async def _generate_embeddings_with_retry(self, task: ProcessingTask, content: str) -> List[Dict[str, Any]]:
        """Generate embeddings with retry logic"""
        for attempt in range(task.max_retries + 1):
            try:
                logger.info(f"Generating embeddings for task {task.task_id} (attempt {attempt + 1})")
                
                # Generate embeddings for content
                embeddings = await self.content_processor.generate_embeddings(content)
                
                return embeddings
                
            except Exception as e:
                if attempt == task.max_retries:
                    raise Exception(f"Failed to generate embeddings after {task.max_retries + 1} attempts: {str(e)}")
                    
                logger.warning(f"Embedding generation failed for task {task.task_id}, attempt {attempt + 1}: {str(e)}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                
    async def _store_results_with_retry(self, task: ProcessingTask, content: str, 
                                      text_analysis: Dict[str, Any], ai_results: Dict[str, Any], 
                                      embeddings: List[Dict[str, Any]]):
        """Store results in database with retry logic"""
        for attempt in range(task.max_retries + 1):
            try:
                logger.info(f"Storing results for task {task.task_id} (attempt {attempt + 1})")
                
                # Prepare document data
                analysis = text_analysis["analysis"]
                chunks = text_analysis["chunks"]
                
                document_data = {
                    "user_id": task.user_id,
                    "source_url": task.url,
                    "title": ai_results.get("title", "Untitled"),
                    "summary": ai_results.get("summary", ""),
                    "tags": ai_results.get("tags", []),
                    "insights": ai_results.get("insights", []),
                    "action_items": ai_results.get("action_items", []),
                    "quotable_snippets": ai_results.get("quotable_snippets", []),
                    "processing_status": "completed",
                    # Enhanced metadata
                    "content_type": analysis.content_type.value,
                    "quality": analysis.quality.value,
                    "language": analysis.language,
                    "word_count": analysis.word_count,
                    "sentence_count": analysis.sentence_count,
                    "paragraph_count": analysis.paragraph_count,
                    "reading_time_minutes": analysis.reading_time_minutes,
                    "complexity_score": analysis.complexity_score,
                    "key_phrases": analysis.key_phrases,
                    "structure": analysis.structure
                }
                
                # Insert document
                result = self.supabase.table("documents").insert(document_data).execute()
                
                if not result.data:
                    raise Exception("Failed to insert document into database")
                    
                document_id = result.data[0]["id"]
                
                # Store chunks with embeddings
                for i, chunk in enumerate(chunks):
                    if i < len(embeddings):
                        chunk_data = {
                            "document_id": document_id,
                            "chunk_index": chunk.index,
                            "content": chunk.text,
                            "embedding": embeddings[i].get("embedding", []),
                            "metadata": {
                                "word_count": chunk.word_count,
                                "sentence_count": chunk.sentence_count,
                                "quality_score": chunk.quality_score,
                                "topics": chunk.topics or [],
                                "key_phrases": chunk.key_phrases or []
                            }
                        }
                        
                        self.supabase.table("document_chunks").insert(chunk_data).execute()
                        
                return document_id
                
            except Exception as e:
                if attempt == task.max_retries:
                    raise Exception(f"Failed to store results after {task.max_retries + 1} attempts: {str(e)}")
                    
                logger.warning(f"Result storage failed for task {task.task_id}, attempt {attempt + 1}: {str(e)}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                
    async def _complete_task(self, task: ProcessingTask, content: str, text_analysis: Dict[str, Any], 
                           ai_results: Dict[str, Any], embeddings: List[Dict[str, Any]]):
        """Complete a processing task"""
        try:
            # Update task status
            task.update_status(ProcessingStatus.COMPLETED, ProcessingStage.COMPLETED, 1.0)
            task.result = {
                "content_length": len(content),
                "chunks_count": len(text_analysis["chunks"]),
                "embeddings_count": len(embeddings),
                "ai_results": ai_results
            }
            
            # Move to completed tasks
            del self.active_tasks[task.task_id]
            self.completed_tasks[task.task_id] = task
            
            # Update metrics
            self.metrics["total_processed"] += 1
            self.metrics["successful"] += 1
            
            if task.start_time and task.end_time:
                processing_time = (task.end_time - task.start_time).total_seconds()
                self.metrics["total_processing_time"] += processing_time
                
            # Update database
            await self._update_database_status(task)
            
            logger.info(f"Completed processing task {task.task_id}")
            
        except Exception as e:
            logger.error(f"Failed to complete task {task.task_id}: {str(e)}")
            await self._handle_task_error(task, str(e))
            
    async def _handle_task_error(self, task: ProcessingTask, error_message: str):
        """Handle task errors"""
        try:
            # Update task status
            task.update_status(ProcessingStatus.FAILED, error_message=error_message)
            
            # Move to failed tasks
            if task.task_id in self.active_tasks:
                del self.active_tasks[task.task_id]
            self.failed_tasks[task.task_id] = task
            
            # Update metrics
            self.metrics["total_processed"] += 1
            self.metrics["failed"] += 1
            
            # Update database
            await self._update_database_status(task)
            
            logger.error(f"Task {task.task_id} failed: {error_message}")
            
        except Exception as e:
            logger.error(f"Failed to handle error for task {task.task_id}: {str(e)}")
            
    async def _update_task_progress(self, task: ProcessingTask, stage: ProcessingStage, progress: float):
        """Update task progress"""
        try:
            task.update_status(ProcessingStatus.PROCESSING, stage, progress)
            await self._update_database_status(task)
            
        except Exception as e:
            logger.warning(f"Failed to update task progress for {task.task_id}: {str(e)}")
            
    async def _update_database_status(self, task: ProcessingTask):
        """Update task status in database"""
        try:
            status_data = {
                "task_id": task.task_id,
                "url": task.url,
                "user_id": task.user_id,
                "status": task.status.value,
                "stage": task.stage.value,
                "progress": task.progress,
                "error_message": task.error_message,
                "start_time": task.start_time.isoformat() if task.start_time else None,
                "end_time": task.end_time.isoformat() if task.end_time else None,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Upsert status
            self.supabase.table("processing_status").upsert(status_data).execute()
            
        except Exception as e:
            logger.warning(f"Failed to update database status for task {task.task_id}: {str(e)}")
            
    async def _get_database_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get task status from database"""
        try:
            result = self.supabase.table("processing_status").select("*").eq("task_id", task_id).execute()
            
            if result.data:
                return result.data[0]
            else:
                return {"error": "Task not found"}
                
        except Exception as e:
            logger.error(f"Failed to get database task status for {task_id}: {str(e)}")
            return {"error": str(e)}
            
    def _task_to_dict(self, task: ProcessingTask) -> Dict[str, Any]:
        """Convert task to dictionary"""
        return {
            "task_id": task.task_id,
            "url": task.url,
            "user_id": task.user_id,
            "status": task.status.value,
            "stage": task.stage.value,
            "progress": task.progress,
            "error_message": task.error_message,
            "start_time": task.start_time.isoformat() if task.start_time else None,
            "end_time": task.end_time.isoformat() if task.end_time else None,
            "retry_count": task.retry_count,
            "result": task.result
        }
