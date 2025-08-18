#!/usr/bin/env python3
"""
Fix embeddings by re-processing existing documents
"""

import sys
sys.path.append('backend')

from backend.services.content_processor import ContentProcessor
from backend.database.client import get_supabase_service_client
import asyncio
import json

async def fix_embeddings():
    """Re-process documents to generate proper chunks and embeddings"""
    
    print("🔧 Fixing Embeddings...")
    print("=" * 40)
    
    try:
        processor = ContentProcessor()
        supabase = get_supabase_service_client()
        
        # Get all documents
        docs_result = supabase.table('documents').select('*').execute()
        print(f"📄 Found {len(docs_result.data)} documents")
        
        # Clear existing embeddings first
        print("🧹 Clearing existing embeddings...")
        supabase.table('embeddings').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
        print("✅ Cleared existing embeddings")
        
        for i, doc in enumerate(docs_result.data, 1):
            print(f"\n🔧 Processing document {i}/{len(docs_result.data)}: {doc['title'][:50]}...")
            
            try:
                # Re-process the content from the source URL
                source_url = doc.get('source_url')
                if not source_url:
                    print(f"⚠️  No source URL for document {doc['id']}")
                    continue
                
                print(f"📡 Re-processing URL: {source_url}")
                
                # Process the content again
                processed_content = await processor.process_url(source_url)
                
                # Update document with new chunks
                update_data = {
                    "content_chunks": processed_content["chunks"],
                    "updated_at": "2025-08-19T00:00:00.000000+00:00"
                }
                
                supabase.table("documents").update(update_data).eq("id", doc['id']).execute()
                print(f"✅ Updated document with {len(processed_content['chunks'])} chunks")
                
                # Generate embeddings for each chunk
                print(f"🔢 Generating embeddings for {len(processed_content['chunks'])} chunks...")
                
                for j, chunk in enumerate(processed_content['chunks']):
                    try:
                        # Generate embedding
                        embedding = await processor._generate_embedding(chunk['text'])
                        
                        # Save to database
                        embedding_data = {
                            "document_id": doc['id'],
                            "chunk_index": chunk['index'],
                            "content": chunk['text'],
                            "embedding": embedding
                        }
                        
                        result = supabase.table("embeddings").insert(embedding_data).execute()
                        
                        # Check if the operation was successful (no exception means success)
                        print(f"    ✅ Saved embedding {j+1}/{len(processed_content['chunks'])}")
                            
                    except Exception as e:
                        print(f"    ❌ Error generating embedding {j+1}: {str(e)}")
                        continue
                
                print(f"✅ Completed document {doc['id']}")
                
            except Exception as e:
                print(f"❌ Error processing document {doc['id']}: {str(e)}")
                continue
        
        print(f"\n🎉 Embedding fix complete!")
        
        # Final verification
        final_docs = supabase.table('documents').select('*').execute()
        final_embeddings = supabase.table('embeddings').select('*').execute()
        
        print(f"📊 Final Status:")
        print(f"  📄 Documents: {len(final_docs.data)}")
        print(f"  🔢 Embeddings: {len(final_embeddings.data)}")
        
        # Check chunks
        for doc in final_docs.data:
            chunks = doc.get('content_chunks', [])
            print(f"  📝 Document {doc['id'][:8]}...: {len(chunks)} chunks")
        
    except Exception as e:
        print(f"❌ Error during embedding fix: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(fix_embeddings())
