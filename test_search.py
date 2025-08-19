#!/usr/bin/env python3

from database.client import get_supabase_service_client

def test_search():
    supabase = get_supabase_service_client()
    result = supabase.table('documents').select('*').execute()
    
    query_terms = ['reading', 'writing', 'connection']
    print(f'Testing search for: {query_terms}')
    
    matches = []
    for doc in result.data:
        score = 0
        title = doc.get('title', '').lower()
        summary = doc.get('summary', '').lower()
        tags = [tag.lower() for tag in doc.get('tags', [])]
        
        # Calculate relevance score
        for term in query_terms:
            if term in title:
                score += 3  # Title matches are most important
            if term in summary:
                score += 2  # Summary matches are important
            if any(term in tag for tag in tags):
                score += 1  # Tag matches are good
        
        if score > 0:
            matches.append({
                'doc': doc,
                'score': score
            })
    
    # Sort by score and limit results
    matches.sort(key=lambda x: x['score'], reverse=True)
    
    print(f'Found {len(matches)} matches:')
    for match in matches:
        doc = match['doc']
        print(f'- {doc["title"]} | Score: {match["score"]} | Tags: {doc.get("tags", [])}')

if __name__ == "__main__":
    test_search()
