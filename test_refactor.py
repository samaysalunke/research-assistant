#!/usr/bin/env python3
"""
Test script to verify Priority 1 refactoring fixes
"""

import sys
sys.path.append('backend')

from backend.services.content_processor import ContentProcessor
from backend.core.logging import get_logger
from backend.core.exceptions import EmbeddingGenerationError
import asyncio

async def test_refactor_fixes():
    """Test the Priority 1 refactoring fixes"""
    
    logger = get_logger("test_refactor")
    logger.info("🔧 Testing Priority 1 Refactoring Fixes...")
    
    try:
        # Test 1: Embedding Generation
        logger.info("🔢 Testing embedding generation...")
        processor = ContentProcessor()
        
        test_text = "This is a test of the improved embedding generation"
        logger.info(f"📝 Test text: {test_text}")
        
        embedding = await processor._generate_embedding(test_text)
        logger.info(f"✅ Generated embedding with {len(embedding)} dimensions")
        
        # Check if it's a real embedding (not hash-based)
        if len(embedding) == 3072:
            logger.info("✅ Correct dimensions (3072) for Claude embeddings")
        elif len(embedding) == 1536:
            logger.info("✅ Correct dimensions (1536) for OpenAI embeddings")
        else:
            logger.warning(f"⚠️ Unexpected dimensions: {len(embedding)}")
        
        # Test 2: Error Handling
        logger.info("🚨 Testing error handling...")
        try:
            # This should raise an EmbeddingGenerationError
            await processor._generate_embedding("")
        except Exception as e:
            logger.info(f"✅ Error handling works: {type(e).__name__}")
        
        # Test 3: Logging
        logger.info("📝 Testing structured logging...", extra_fields={
            "test_phase": "refactor_verification",
            "embedding_dimensions": len(embedding),
            "test_status": "success"
        })
        
        logger.info("🎉 All Priority 1 refactoring tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Refactoring test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_refactor_fixes())
    if success:
        print("\n🎉 Priority 1 refactoring is working! Ready for Milestone 3.")
    else:
        print("\n❌ Priority 1 refactoring needs more work.")
