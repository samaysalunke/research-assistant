import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Upload, FileText, Link, Loader2, CheckCircle, XCircle } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import toast from 'react-hot-toast';

interface ProcessingStatus {
  job_id: string;
  status: string;
  message: string;
  progress?: number;
  result?: any;
  error?: string;
}

const Dashboard: React.FC = () => {
  const { session } = useAuth();
  const [url, setUrl] = useState('');
  const [text, setText] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingJobs, setProcessingJobs] = useState<ProcessingStatus[]>([]);

  const ingestUrl = async () => {
    if (!url.trim()) return;

    setIsProcessing(true);
    const jobId = Date.now().toString();

    // Add to processing jobs
    setProcessingJobs(prev => [...prev, {
      job_id: jobId,
      status: 'processing',
      message: 'Processing URL...',
      progress: 0
    }]);

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/ingest/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('supabase.auth.token')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: url.trim(),
          content_type: 'url'
        }),
      });

      if (response.ok) {
        const result = await response.json();
        setProcessingJobs(prev => prev.map(job => 
          job.job_id === jobId 
            ? { ...job, status: 'completed', message: result.message || 'Processing completed!' }
            : job
        ));
        toast.success(result.message || 'Content is already being processed');
        setUrl('');
      } else {
        throw new Error('Failed to process URL');
      }
    } catch (error) {
      setProcessingJobs(prev => prev.map(job => 
        job.job_id === jobId 
          ? { ...job, status: 'error', error: 'Processing failed' }
          : job
      ));
      toast.error('Failed to process URL');
    } finally {
      setIsProcessing(false);
    }
  };

  const ingestText = async () => {
    if (!text.trim()) return;

    setIsProcessing(true);
    const jobId = Date.now().toString();

    setProcessingJobs(prev => [...prev, {
      job_id: jobId,
      status: 'processing',
      message: 'Processing text...',
      progress: 0
    }]);

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/ingest/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('supabase.auth.token')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: text.trim(),
          content_type: 'text'
        }),
      });

      if (response.ok) {
        const result = await response.json();
        setProcessingJobs(prev => prev.map(job => 
          job.job_id === jobId 
            ? { ...job, status: 'completed', message: result.message || 'Processing completed!' }
            : job
        ));
        toast.success('Text processed successfully!');
        setText('');
      } else {
        throw new Error('Failed to process text');
      }
    } catch (error) {
      setProcessingJobs(prev => prev.map(job => 
        job.job_id === jobId 
          ? { ...job, status: 'error', error: 'Processing failed' }
          : job
      ));
      toast.error('Failed to process text');
    } finally {
      setIsProcessing(false);
    }
  };

  const removeJob = (jobId: string) => {
    setProcessingJobs(prev => prev.filter(job => job.job_id !== jobId));
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'processing':
        return <Loader2 className="h-4 w-4 animate-spin" />;
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'error':
        return <XCircle className="h-4 w-4 text-red-600" />;
      default:
        return <FileText className="h-4 w-4" />;
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-3">
        <Upload className="h-8 w-8 text-blue-600" />
        <div>
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <p className="text-gray-600">Ingest content from URLs or direct text input</p>
        </div>
      </div>

      {/* URL Ingestion */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Link className="h-5 w-5" />
            <span>Ingest from URL</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex space-x-2">
            <Input
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="Enter URL to process..."
              disabled={isProcessing}
              className="flex-1"
            />
            <Button
              onClick={ingestUrl}
              disabled={!url.trim() || isProcessing}
              className="flex items-center space-x-2"
            >
              <Upload className="h-4 w-4" />
              <span>Process</span>
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Text Ingestion */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <FileText className="h-5 w-5" />
            <span>Ingest Text</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Enter text content to process..."
              disabled={isProcessing}
              className="w-full h-32 p-3 border rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <div className="flex justify-end">
              <Button
                onClick={ingestText}
                disabled={!text.trim() || isProcessing}
                className="flex items-center space-x-2"
              >
                <Upload className="h-4 w-4" />
                <span>Process</span>
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Processing Status */}
      {processingJobs.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Processing Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {processingJobs.map((job) => (
                <div key={job.job_id} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center space-x-3">
                    {getStatusIcon(job.status)}
                    <div>
                      <p className="font-medium">{job.message}</p>
                      {job.error && (
                        <p className="text-sm text-red-600">{job.error}</p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Badge variant={job.status === 'completed' ? 'default' : job.status === 'error' ? 'destructive' : 'secondary'}>
                      {job.status}
                    </Badge>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => removeJob(job.job_id)}
                    >
                      <XCircle className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default Dashboard;
