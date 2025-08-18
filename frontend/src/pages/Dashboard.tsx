import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import toast from 'react-hot-toast';
import { 
  DocumentPlusIcon, 
  LinkIcon, 
  DocumentTextIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon
} from '@heroicons/react/24/outline';

interface ProcessingJob {
  id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  title: string;
  url?: string;
  createdAt: string;
}

const Dashboard: React.FC = () => {
  const { user, session } = useAuth();
  const [url, setUrl] = useState('');
  const [text, setText] = useState('');
  const [activeTab, setActiveTab] = useState<'url' | 'text'>('url');
  const [loading, setLoading] = useState(false);
  const [jobs, setJobs] = useState<ProcessingJob[]>([]);

  const handleUrlSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) {
      toast.error('Please enter a URL');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/ingest/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session?.access_token}`,
        },
        body: JSON.stringify({ source_url: url }),
      });

      if (!response.ok) {
        throw new Error('Failed to submit URL');
      }

      const result = await response.json();
      
      // Add job to list
      setJobs(prev => [{
        id: result.job_id,
        status: 'pending',
        title: 'Processing...',
        url,
        createdAt: new Date().toISOString(),
      }, ...prev]);

      toast.success('Content submitted for processing!');
      setUrl('');
    } catch (error: any) {
      toast.error(error.message || 'Failed to submit content');
    } finally {
      setLoading(false);
    }
  };

  const handleTextSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim()) {
      toast.error('Please enter some text');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/ingest/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session?.access_token}`,
        },
        body: JSON.stringify({ text }),
      });

      if (!response.ok) {
        throw new Error('Failed to submit text');
      }

      const result = await response.json();
      
      setJobs(prev => [{
        id: result.job_id,
        status: 'pending',
        title: 'Processing...',
        createdAt: new Date().toISOString(),
      }, ...prev]);

      toast.success('Content submitted for processing!');
      setText('');
    } catch (error: any) {
      toast.error(error.message || 'Failed to submit content');
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending':
        return <ClockIcon className="w-5 h-5 text-yellow-500" />;
      case 'processing':
        return <ClockIcon className="w-5 h-5 text-blue-500 animate-spin" />;
      case 'completed':
        return <CheckCircleIcon className="w-5 h-5 text-green-500" />;
      case 'failed':
        return <XCircleIcon className="w-5 h-5 text-red-500" />;
      default:
        return <ClockIcon className="w-5 h-5 text-gray-500" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600">Add new content to your research library</p>
      </div>

      {/* Content Input */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex space-x-4 mb-6">
          <button
            onClick={() => setActiveTab('url')}
            className={`flex items-center px-4 py-2 rounded-md transition-colors ${
              activeTab === 'url'
                ? 'bg-blue-100 text-blue-700'
                : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            <LinkIcon className="w-5 h-5 mr-2" />
            Add URL
          </button>
          <button
            onClick={() => setActiveTab('text')}
            className={`flex items-center px-4 py-2 rounded-md transition-colors ${
              activeTab === 'text'
                ? 'bg-blue-100 text-blue-700'
                : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            <DocumentTextIcon className="w-5 h-5 mr-2" />
            Add Text
          </button>
        </div>

        {activeTab === 'url' ? (
          <form onSubmit={handleUrlSubmit} className="space-y-4">
            <div>
              <label htmlFor="url" className="block text-sm font-medium text-gray-700 mb-2">
                Website URL
              </label>
              <input
                type="url"
                id="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://example.com/article"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
            >
              <DocumentPlusIcon className="w-5 h-5 mr-2" />
              {loading ? 'Processing...' : 'Add Content'}
            </button>
          </form>
        ) : (
          <form onSubmit={handleTextSubmit} className="space-y-4">
            <div>
              <label htmlFor="text" className="block text-sm font-medium text-gray-700 mb-2">
                Text Content
              </label>
              <textarea
                id="text"
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Paste your text content here..."
                rows={6}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
            >
              <DocumentPlusIcon className="w-5 h-5 mr-2" />
              {loading ? 'Processing...' : 'Add Content'}
            </button>
          </form>
        )}
      </div>

      {/* Processing Jobs */}
      {jobs.length > 0 && (
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900">Processing Jobs</h2>
          </div>
          <div className="divide-y divide-gray-200">
            {jobs.map((job) => (
              <div key={job.id} className="px-6 py-4 flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  {getStatusIcon(job.status)}
                  <div>
                    <p className="text-sm font-medium text-gray-900">{job.title}</p>
                    {job.url && (
                      <p className="text-xs text-gray-500 truncate max-w-xs">{job.url}</p>
                    )}
                  </div>
                </div>
                <div className="text-xs text-gray-500">
                  {new Date(job.createdAt).toLocaleTimeString()}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
