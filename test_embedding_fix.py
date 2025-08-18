#!/usr/bin/env python3
"""
Test and fix embedding generation
"""

import sys
sys.path.append('backend')

from backend.services.content_processor import ContentProcessor
import asyncio

async def test_embedding():
    """Test embedding generation"""
    
    print("🔢 Testing Embedding Generation...")
    print("=" * 40)
    
    try:
        processor = ContentProcessor()
        
        # Test text
        test_text = "This is a test of embedding generation"
        print(f"📝 Test text: {test_text}")
        
        # Try to generate embedding
        print("🔢 Generating embedding...")
        embedding = await processor._generate_embedding(test_text)
        
        print(f"✅ Success! Generated embedding with {len(embedding)} dimensions")
        print(f"📊 First 5 values: {embedding[:5]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_embedding())
    if success:
        print("\n🎉 Embedding generation works! Now run: python3 fix_embeddings.py")
    else:
        print("\n❌ Embedding generation failed. Check the error above.")
