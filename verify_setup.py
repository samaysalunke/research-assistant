#!/usr/bin/env python3
"""
Verify that embeddings were created and semantic search works
"""

import sys
sys.path.append('backend')

from backend.services.content_processor import ContentProcessor
from backend.database.client import get_supabase_service_client
import asyncio

async def verify_setup():
    """Verify embeddings and test semantic search"""
    
    print("🔍 Verifying Setup...")
    print("=" * 40)
    
    try:
        processor = ContentProcessor()
        supabase = get_supabase_service_client()
        
        # Check documents
        docs_result = supabase.table('documents').select('*').execute()
        print(f"📄 Documents: {len(docs_result.data)}")
        
        # Check embeddings
        embeddings_result = supabase.table('embeddings').select('*').execute()
        print(f"🔢 Embeddings: {len(embeddings_result.data)}")
        
        if len(embeddings_result.data) == 0:
            print("❌ No embeddings found! Run: python3 fix_embeddings.py")
            return
        
        # Check chunks
        total_chunks = 0
        for doc in docs_result.data:
            chunks = doc.get('content_chunks', [])
            total_chunks += len(chunks)
            print(f"  📝 Document {doc['id'][:8]}...: {len(chunks)} chunks")
        
        print(f"📊 Total chunks: {total_chunks}")
        
        if total_chunks == 0:
            print("❌ No content chunks found! Run: python3 fix_embeddings.py")
            return
        
        # Test semantic search
        print(f"\n🔍 Testing Semantic Search...")
        print("-" * 30)
        
        test_query = "What is LangExtract?"
        print(f"Query: {test_query}")
        
        # Generate embedding for query
        query_embedding = await processor._generate_embedding(test_query)
        print(f"✅ Generated query embedding: {len(query_embedding)} dimensions")
        
        # Perform search
        search_result = supabase.rpc(
            'semantic_search',
            {
                'query_embedding': query_embedding,
                'similarity_threshold': 0.7,
                'match_count': 5
            }
        ).execute()
        
        if search_result.data:
            print(f"✅ Found {len(search_result.data)} results:")
            for i, result in enumerate(search_result.data[:3], 1):
                similarity = result.get('similarity', 0)
                content = result.get('content', '')[:100]
                print(f"  {i}. Similarity: {similarity:.3f}")
                print(f"     Content: {content}...")
                print()
        else:
            print("⚠️  No search results found")
        
        print("🎉 Setup verification complete!")
        print("\n🚀 Ready for semantic search testing!")
        
    except Exception as e:
        print(f"❌ Error during verification: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(verify_setup())
