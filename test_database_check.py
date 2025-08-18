#!/usr/bin/env python3
"""
Quick database check to see what documents we have
"""

import sys
sys.path.append('backend')

from backend.database.client import get_supabase_service_client

def check_database():
    """Check what documents are in the database"""
    
    print("📊 Database Check...")
    print("=" * 30)
    
    try:
        supabase = get_supabase_service_client()
        
        # Check documents
        docs_result = supabase.table('documents').select('*').execute()
        print(f"📄 Documents found: {len(docs_result.data)}")
        
        for doc in docs_result.data:
            print(f"  - ID: {doc['id']}")
            print(f"    Title: {doc['title']}")
            print(f"    Source URL: {doc.get('source_url', 'N/A')}")
            print(f"    Tags: {doc.get('tags', [])}")
            print(f"    Insights: {len(doc.get('insights', []))} items")
            print(f"    Status: {doc.get('processing_status', 'N/A')}")
            print()
        
        # Check embeddings
        embeddings_result = supabase.table('embeddings').select('*').execute()
        print(f"🔢 Embeddings found: {len(embeddings_result.data)}")
        
        if embeddings_result.data:
            print(f"  - First embedding dimensions: {len(embeddings_result.data[0]['embedding'])}")
            print(f"  - Document IDs: {[e['document_id'] for e in embeddings_result.data]}")
        
        print("✅ Database check complete!")
        
    except Exception as e:
        print(f"❌ Error during database check: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_database()
