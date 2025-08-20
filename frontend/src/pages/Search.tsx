import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Search as SearchIcon, Filter, ExternalLink, FileText } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';

interface SearchResult {
  id: string;
  document_id: string;
  chunk_index: number;
  content: string;
  similarity: number;
  keyword_rank: number;
  document_title: string;
  document_url?: string;
}

interface SearchResponse {
  results: SearchResult[];
  total_count: number;
  query: string;
  search_type: string;
}

const Search: React.FC = () => {
  const { session } = useAuth();
  const [query, setQuery] = useState('');
  const [searchType, setSearchType] = useState<'keyword' | 'semantic' | 'hybrid'>('keyword');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [totalCount, setTotalCount] = useState(0);

  const performSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/search/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('supabase.auth.token')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query.trim(),
          search_type: searchType,
          limit: 20
        }),
      });

      if (response.ok) {
        const data: SearchResponse = await response.json();
        setResults(data.results || []);
        setTotalCount(data.total_count || 0);
      } else {
        console.error('Search failed');
        setResults([]);
        setTotalCount(0);
      }
    } catch (error) {
      console.error('Search error:', error);
      setResults([]);
      setTotalCount(0);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    performSearch();
  };

  const formatSimilarity = (similarity: number) => {
    return Math.round(similarity * 100);
  };

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-3">
        <SearchIcon className="h-8 w-8 text-blue-600" />
        <div>
          <h1 className="text-2xl font-bold">Search</h1>
          <p className="text-gray-600">Search through your processed documents</p>
        </div>
      </div>

      {/* Search Form */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <SearchIcon className="h-5 w-5" />
            <span>Search Documents</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Search Input */}
            <div className="flex space-x-2">
              <Input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Enter your search query..."
                className="flex-1"
                disabled={loading}
              />
              <Button type="submit" disabled={!query.trim() || loading}>
                {loading ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                ) : (
                  <SearchIcon className="h-4 w-4" />
                )}
              </Button>
            </div>

            {/* Search Type Selection */}
            <div className="flex items-center space-x-4">
              <span className="text-sm font-medium">Search Type:</span>
              <div className="flex space-x-2">
                {(['keyword', 'semantic', 'hybrid'] as const).map((type) => (
                  <Button
                    key={type}
                    type="button"
                    variant={searchType === type ? "default" : "outline"}
                    size="sm"
                    onClick={() => setSearchType(type)}
                    disabled={loading}
                  >
                    {type.charAt(0).toUpperCase() + type.slice(1)}
                  </Button>
                ))}
              </div>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* Results */}
      {results.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Search Results</span>
              <Badge variant="secondary">
                {totalCount} result{totalCount !== 1 ? 's' : ''}
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {results.map((result, index) => (
                <div key={result.id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="font-medium text-lg line-clamp-2">
                      {result.document_title}
                    </h3>
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline">
                        {formatSimilarity(result.similarity)}% match
                      </Badge>
                      {result.document_url && (
                        <a
                          href={result.document_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:text-blue-700"
                        >
                          <ExternalLink className="h-4 w-4" />
                        </a>
                      )}
                    </div>
                  </div>
                  
                  <p className="text-gray-600 mb-3 line-clamp-3">
                    {result.content}
                  </p>
                  
                  <div className="flex items-center justify-between text-sm text-gray-500">
                    <span>Chunk {result.chunk_index + 1}</span>
                    <div className="flex items-center space-x-4">
                      <span>Similarity: {formatSimilarity(result.similarity)}%</span>
                      <span>Keyword Rank: {formatSimilarity(result.keyword_rank)}%</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* No Results */}
      {!loading && query && results.length === 0 && (
        <Card>
          <CardContent className="text-center py-12">
            <SearchIcon className="h-12 w-12 mx-auto mb-4 text-gray-300" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No results found</h3>
            <p className="text-gray-500">
              Try adjusting your search query or search type
            </p>
          </CardContent>
        </Card>
      )}

      {/* Search Tips */}
      {!query && (
        <Card>
          <CardHeader>
            <CardTitle>Search Tips</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-start space-x-3">
                <Badge variant="outline">Keyword</Badge>
                <p className="text-sm text-gray-600">
                  Traditional text search that matches exact words and phrases
                </p>
              </div>
              <div className="flex items-start space-x-3">
                <Badge variant="outline">Semantic</Badge>
                <p className="text-sm text-gray-600">
                  AI-powered search that understands meaning and context
                </p>
              </div>
              <div className="flex items-start space-x-3">
                <Badge variant="outline">Hybrid</Badge>
                <p className="text-sm text-gray-600">
                  Combines both keyword and semantic search for best results
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default Search;
