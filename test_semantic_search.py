#!/usr/bin/env python3
"""
Test script for semantic search functionality
"""

import sys
import os
sys.path.append('backend')

from backend.services.content_processor import ContentProcessor
from backend.database.client import get_supabase_service_client
import asyncio

async def test_semantic_search():
    """Test semantic search with various queries"""
    
    print("🔍 Testing Semantic Search...")
    print("=" * 50)
    
    try:
        # Initialize components
        processor = ContentProcessor()
        supabase = get_supabase_service_client()
        
        print("✅ Components initialized")
        
        # Test queries
        test_queries = [
            "What is LangExtract?",
            "How does information extraction work?",
            "What are the key features?",
            "Tell me about source grounding"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"🔍 Query {i}: {query}")
            print("-" * 40)
            
            try:
                # Generate embedding for the query
                query_embedding = await processor._generate_embedding(query)
                print(f"✅ Generated embedding: {len(query_embedding)} dimensions")
                
                # Perform semantic search
                search_result = supabase.rpc(
                    'semantic_search',
                    {
                        'query_embedding': query_embedding,
                        'similarity_threshold': 0.7,
                        'match_count': 5
                    }
                ).execute()
                
                if search_result.data:
                    print(f"✅ Found {len(search_result.data)} relevant results:")
                    for j, result in enumerate(search_result.data[:3], 1):
                        print(f"  {j}. Similarity: {result.get('similarity', 0):.3f}")
                        print(f"     Content: {result.get('content', '')[:100]}...")
                        print()
                else:
                    print("⚠️  No results found")
                    print()
                    
            except Exception as e:
                print(f"❌ Error with query '{query}': {str(e)}")
                print()
        
        print("🎉 Semantic Search Testing Complete!")
        
    except Exception as e:
        print(f"❌ Error during semantic search test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_semantic_search())
