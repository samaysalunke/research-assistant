import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import toast from 'react-hot-toast';
import { MagnifyingGlassIcon, DocumentTextIcon, TagIcon } from '@heroicons/react/24/outline';

interface SearchResult {
  id: string;
  document_id: string;
  chunk_index: number;
  content: string;
  similarity: number;
  title?: string;
  source_url?: string;
}

const Search: React.FC = () => {
  const { user, session } = useAuth();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchType, setSearchType] = useState<'semantic' | 'hybrid'>('semantic');

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) {
      toast.error('Please enter a search query');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('${import.meta.env.VITE_API_URL}/api/v1/search/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session?.access_token}`,
        },
        body: JSON.stringify({
          query: query,
          search_type: searchType,
          limit: 10,
        }),
      });

      if (!response.ok) {
        throw new Error('Search failed');
      }

      const data = await response.json();
      setResults(data.results || []);
      
      if (data.results?.length === 0) {
        toast.info('No results found. Try a different query.');
      }
    } catch (error: any) {
      toast.error(error.message || 'Search failed');
    } finally {
      setLoading(false);
    }
  };

  const formatSimilarity = (similarity: number) => {
    return `${(similarity * 100).toFixed(1)}%`;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Search</h1>
        <p className="text-gray-600">Search through your research library</p>
      </div>

      {/* Search Form */}
      <div className="bg-white rounded-lg shadow p-6">
        <form onSubmit={handleSearch} className="space-y-4">
          <div>
            <label htmlFor="query" className="block text-sm font-medium text-gray-700 mb-2">
              Search Query
            </label>
            <div className="flex space-x-4">
              <input
                type="text"
                id="query"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="What would you like to know?"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
              <button
                type="submit"
                disabled={loading}
                className="flex items-center px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
              >
                <MagnifyingGlassIcon className="w-5 h-5 mr-2" />
                {loading ? 'Searching...' : 'Search'}
              </button>
            </div>
          </div>

          <div className="flex space-x-4">
            <label className="flex items-center">
              <input
                type="radio"
                value="semantic"
                checked={searchType === 'semantic'}
                onChange={(e) => setSearchType(e.target.value as 'semantic' | 'hybrid')}
                className="mr-2"
              />
              <span className="text-sm text-gray-700">Semantic Search</span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                value="hybrid"
                checked={searchType === 'hybrid'}
                onChange={(e) => setSearchType(e.target.value as 'semantic' | 'hybrid')}
                className="mr-2"
              />
              <span className="text-sm text-gray-700">Hybrid Search</span>
            </label>
          </div>
        </form>
      </div>

      {/* Search Results */}
      {results.length > 0 && (
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900">
              Search Results ({results.length})
            </h2>
          </div>
          <div className="divide-y divide-gray-200">
            {results.map((result, index) => (
              <div key={result.id} className="p-6">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <DocumentTextIcon className="w-5 h-5 text-gray-400" />
                    <span className="text-sm text-gray-500">
                      Result {index + 1} • {formatSimilarity(result.similarity)} match
                    </span>
                  </div>
                  {result.source_url && (
                    <a
                      href={result.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-blue-600 hover:text-blue-500"
                    >
                      View Source
                    </a>
                  )}
                </div>
                
                <div className="prose max-w-none">
                  <p className="text-gray-900 leading-relaxed">
                    {result.content}
                  </p>
                </div>

                {result.title && (
                  <div className="mt-3 flex items-center space-x-2">
                    <TagIcon className="w-4 h-4 text-gray-400" />
                    <span className="text-sm text-gray-600">{result.title}</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* No Results */}
      {!loading && results.length === 0 && query && (
        <div className="bg-white rounded-lg shadow p-6 text-center">
          <DocumentTextIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No results found</h3>
          <p className="text-gray-600">
            Try adjusting your search terms or adding more content to your library.
          </p>
        </div>
      )}
    </div>
  );
};

export default Search;
