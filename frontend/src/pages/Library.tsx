import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import toast from 'react-hot-toast';
import { 
  DocumentTextIcon, 
  LinkIcon, 
  TagIcon, 
  CalendarIcon,
  TrashIcon,
  EyeIcon
} from '@heroicons/react/24/outline';

interface Document {
  id: string;
  title: string;
  summary?: string;
  source_url?: string;
  tags?: string[];
  insights?: Array<{ text: string; relevance_score: number }>;
  processing_status: string;
  created_at: string;
  updated_at: string;
}

const Library: React.FC = () => {
  const { user, session } = useAuth();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/documents/`, {
        headers: {
          'Authorization': `Bearer ${session?.access_token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch documents');
      }

      const data = await response.json();
      console.log('API Response:', data);
      console.log('Documents:', data.items);
      setDocuments(data.items || []);
    } catch (error: any) {
      toast.error(error.message || 'Failed to fetch documents');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteDocument = async (documentId: string) => {
    if (!confirm('Are you sure you want to delete this document?')) {
      return;
    }

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/documents/${documentId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${session?.access_token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to delete document');
      }

      setDocuments(prev => prev.filter(doc => doc.id !== documentId));
      toast.success('Document deleted successfully');
    } catch (error: any) {
      toast.error(error.message || 'Failed to delete document');
    }
  };

  const getAllTags = () => {
    const allTags = new Set<string>();
    documents.forEach(doc => {
      if (doc.tags) {
        doc.tags.forEach(tag => allTags.add(tag));
      }
    });
    return Array.from(allTags).sort();
  };

  const filteredDocuments = documents.filter(doc => {
    // Filter by search term
    if (searchTerm && !doc.title.toLowerCase().includes(searchTerm.toLowerCase()) &&
        !(doc.summary && doc.summary.toLowerCase().includes(searchTerm.toLowerCase()))) {
      return false;
    }

    // Filter by selected tags
    if (selectedTags.length > 0 && !(doc.tags && selectedTags.some(tag => doc.tags.includes(tag)))) {
      return false;
    }

    return true;
  });

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Library</h1>
        <p className="text-gray-600">Browse and manage your research documents</p>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Search */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search Documents
            </label>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search by title or summary..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Tags Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Filter by Tags
            </label>
            <div className="flex flex-wrap gap-2">
              {getAllTags().map(tag => (
                <button
                  key={tag}
                  onClick={() => setSelectedTags(prev => 
                    prev.includes(tag) 
                      ? prev.filter(t => t !== tag)
                      : [...prev, tag]
                  )}
                  className={`px-3 py-1 text-sm rounded-full transition-colors ${
                    selectedTags.includes(tag)
                      ? 'bg-blue-100 text-blue-700'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {tag}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Documents Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredDocuments.map((doc) => (
          <div key={doc.id} className="bg-white rounded-lg shadow hover:shadow-md transition-shadow">
            <div className="p-6">
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-2">
                  {doc.source_url ? (
                    <LinkIcon className="w-5 h-5 text-blue-500" />
                  ) : (
                    <DocumentTextIcon className="w-5 h-5 text-gray-500" />
                  )}
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    doc.processing_status === 'completed' 
                      ? 'bg-green-100 text-green-700'
                      : doc.processing_status === 'processing'
                      ? 'bg-yellow-100 text-yellow-700'
                      : 'bg-red-100 text-red-700'
                  }`}>
                    {doc.processing_status}
                  </span>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => window.open(doc.source_url, '_blank')}
                    disabled={!doc.source_url}
                    className="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-50"
                    title="View source"
                  >
                    <EyeIcon className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDeleteDocument(doc.id)}
                    className="p-1 text-gray-400 hover:text-red-600"
                    title="Delete document"
                  >
                    <TrashIcon className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Title */}
              <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
                {doc.title}
              </h3>

              {/* Summary */}
              {doc.summary && (
                <p className="text-gray-600 text-sm mb-4 line-clamp-3">
                  {doc.summary}
                </p>
              )}

              {/* Tags */}
              {doc.tags && doc.tags.length > 0 && (
                <div className="flex flex-wrap gap-1 mb-4">
                  {doc.tags.slice(0, 3).map(tag => (
                    <span
                      key={tag}
                      className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded-full"
                    >
                      {tag}
                    </span>
                  ))}
                  {doc.tags.length > 3 && (
                    <span className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded-full">
                      +{doc.tags.length - 3} more
                    </span>
                  )}
                </div>
              )}

              {/* Insights */}
              {doc.insights && doc.insights.length > 0 && (
                <div className="mb-4">
                  <h4 className="text-sm font-medium text-gray-900 mb-2">Key Insights</h4>
                  <ul className="space-y-1">
                    {doc.insights.slice(0, 2).map((insight, index) => (
                      <li key={index} className="text-xs text-gray-600 line-clamp-2">
                        • {insight.text}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Date */}
              <div className="flex items-center text-xs text-gray-500">
                <CalendarIcon className="w-4 h-4 mr-1" />
                Added {formatDate(doc.created_at)}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {filteredDocuments.length === 0 && !loading && (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <DocumentTextIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            {documents.length === 0 ? 'No documents yet' : 'No documents match your filters'}
          </h3>
          <p className="text-gray-600">
            {documents.length === 0 
              ? 'Start by adding some content to your library from the Dashboard.'
              : 'Try adjusting your search terms or tag filters.'
            }
          </p>
        </div>
      )}
    </div>
  );
};

export default Library;
