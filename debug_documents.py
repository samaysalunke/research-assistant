#!/usr/bin/env python3
"""
Debug script to examine document content in database
"""

import sys
sys.path.append('backend')

from backend.database.client import get_supabase_service_client
import json

def debug_documents():
    """Examine document content in detail"""
    
    print("🔍 Debugging Documents...")
    print("=" * 40)
    
    try:
        supabase = get_supabase_service_client()
        
        # Get all documents with all fields
        docs_result = supabase.table('documents').select('*').execute()
        print(f"📄 Found {len(docs_result.data)} documents")
        
        for i, doc in enumerate(docs_result.data, 1):
            print(f"\n📄 Document {i}:")
            print(f"  ID: {doc['id']}")
            print(f"  Title: {doc['title']}")
            print(f"  Source URL: {doc.get('source_url', 'N/A')}")
            print(f"  Status: {doc.get('processing_status', 'N/A')}")
            print(f"  Created: {doc.get('created_at', 'N/A')}")
            print(f"  Updated: {doc.get('updated_at', 'N/A')}")
            
            # Check content_chunks
            chunks = doc.get('content_chunks')
            if chunks:
                print(f"  📝 Content Chunks: {len(chunks)} chunks")
                if isinstance(chunks, list) and len(chunks) > 0:
                    print(f"    First chunk: {chunks[0].get('text', 'NO TEXT')[:100]}...")
                else:
                    print(f"    Chunks data: {type(chunks)} - {chunks}")
            else:
                print(f"  ❌ No content_chunks field")
            
            # Check other fields
            print(f"  🏷️  Tags: {doc.get('tags', [])}")
            print(f"  💡 Insights: {len(doc.get('insights', []))} items")
            print(f"  📋 Action Items: {len(doc.get('action_items', []))} items")
            print(f"  💬 Quotable Snippets: {len(doc.get('quotable_snippets', []))} items")
            
            # Show summary if available
            summary = doc.get('summary')
            if summary:
                print(f"  📄 Summary: {summary[:200]}...")
            
            print("-" * 50)
        
    except Exception as e:
        print(f"❌ Error during debug: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_documents()
