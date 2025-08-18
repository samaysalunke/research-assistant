#!/usr/bin/env python3
"""
Generate embeddings for existing documents that don't have embeddings
"""

import sys
sys.path.append('backend')

from backend.services.content_processor import ContentProcessor
from backend.database.client import get_supabase_service_client
import asyncio

async def generate_missing_embeddings():
    """Generate embeddings for documents that don't have them"""
    
    print("🔢 Generating Missing Embeddings...")
    print("=" * 40)
    
    try:
        processor = ContentProcessor()
        supabase = get_supabase_service_client()
        
        # Get all documents
        docs_result = supabase.table('documents').select('*').execute()
        print(f"📄 Found {len(docs_result.data)} documents")
        
        # Get existing embeddings
        embeddings_result = supabase.table('embeddings').select('document_id').execute()
        existing_doc_ids = set(e['document_id'] for e in embeddings_result.data)
        print(f"🔢 Documents with embeddings: {len(existing_doc_ids)}")
        
        # Find documents without embeddings
        missing_docs = [doc for doc in docs_result.data if doc['id'] not in existing_doc_ids]
        print(f"⚠️  Documents missing embeddings: {len(missing_docs)}")
        
        if not missing_docs:
            print("✅ All documents already have embeddings!")
            return
        
        # Generate embeddings for missing documents
        for i, doc in enumerate(missing_docs, 1):
            print(f"\n🔢 Processing document {i}/{len(missing_docs)}: {doc['title'][:50]}...")
            
            try:
                # Get content chunks
                chunks = doc.get('content_chunks', [])
                if not chunks:
                    print(f"⚠️  No content chunks found for document {doc['id']}")
                    continue
                
                print(f"📝 Found {len(chunks)} content chunks")
                
                # Generate embeddings for each chunk
                for j, chunk in enumerate(chunks):
                    print(f"  Generating embedding {j+1}/{len(chunks)}...")
                    
                    try:
                        # Generate embedding
                        embedding = await processor._generate_embedding(chunk['text'])
                        print(f"    ✅ Generated embedding: {len(embedding)} dimensions")
                        
                        # Save to database
                        embedding_data = {
                            "document_id": doc['id'],
                            "chunk_index": chunk['index'],
                            "content": chunk['text'],
                            "embedding": embedding
                        }
                        
                        result = supabase.table("embeddings").insert(embedding_data).execute()
                        
                        if result.error:
                            print(f"    ❌ Failed to save embedding: {result.error}")
                        else:
                            print(f"    ✅ Saved embedding to database")
                            
                    except Exception as e:
                        print(f"    ❌ Error generating embedding for chunk {j}: {str(e)}")
                        continue
                
                print(f"✅ Completed document {doc['id']}")
                
            except Exception as e:
                print(f"❌ Error processing document {doc['id']}: {str(e)}")
                continue
        
        print(f"\n🎉 Embedding generation complete!")
        
        # Final count
        final_embeddings = supabase.table('embeddings').select('*').execute()
        print(f"📊 Total embeddings in database: {len(final_embeddings.data)}")
        
    except Exception as e:
        print(f"❌ Error during embedding generation: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(generate_missing_embeddings())
