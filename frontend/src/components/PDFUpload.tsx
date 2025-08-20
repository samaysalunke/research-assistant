import React, { useState, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Upload, FileText, CheckCircle, XCircle, Loader2, Download } from 'lucide-react';

interface UploadStatus {
  id: string;
  filename: string;
  status: 'uploading' | 'processing' | 'completed' | 'error';
  progress: number;
  message?: string;
  error?: string;
}

const PDFUpload: React.FC = () => {
  const [uploads, setUploads] = useState<UploadStatus[]>([]);
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (files: FileList | null) => {
    if (!files) return;
    
    Array.from(files).forEach(file => {
      if (file.type === 'application/pdf') {
        uploadFile(file);
      }
    });
  };

  const uploadFile = async (file: File) => {
    const uploadId = Date.now().toString();
    const uploadStatus: UploadStatus = {
      id: uploadId,
      filename: file.name,
      status: 'uploading',
      progress: 0,
    };

    setUploads(prev => [...prev, uploadStatus]);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/ingest/pdf`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('supabase.auth.token')}`,
        },
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        setUploads(prev => prev.map(upload => 
          upload.id === uploadId 
            ? { ...upload, status: 'processing', progress: 50, message: 'Processing PDF...' }
            : upload
        ));

        // Poll for status
        pollProcessingStatus(result.job_id, uploadId);
      } else {
        throw new Error('Upload failed');
      }
    } catch (error) {
      setUploads(prev => prev.map(upload => 
        upload.id === uploadId 
          ? { ...upload, status: 'error', progress: 0, error: 'Upload failed' }
          : upload
      ));
    }
  };

  const pollProcessingStatus = async (jobId: string, uploadId: string) => {
    const maxAttempts = 60; // 5 minutes with 5-second intervals
    let attempts = 0;

    const poll = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/ingest/${jobId}/status`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('supabase.auth.token')}`,
          },
        });

        if (response.ok) {
          const status = await response.json();
          
          if (status.status === 'completed') {
            setUploads(prev => prev.map(upload => 
              upload.id === uploadId 
                ? { ...upload, status: 'completed', progress: 100, message: 'Processing completed!' }
                : upload
            ));
            return;
          } else if (status.status === 'failed') {
            setUploads(prev => prev.map(upload => 
              upload.id === uploadId 
                ? { ...upload, status: 'error', progress: 0, error: status.message || 'Processing failed' }
                : upload
            ));
            return;
          } else {
            // Still processing
            setUploads(prev => prev.map(upload => 
              upload.id === uploadId 
                ? { ...upload, progress: Math.min(upload.progress + 10, 90) }
                : upload
            ));
          }
        }

        attempts++;
        if (attempts < maxAttempts) {
          setTimeout(poll, 5000);
        } else {
          setUploads(prev => prev.map(upload => 
            upload.id === uploadId 
              ? { ...upload, status: 'error', progress: 0, error: 'Processing timeout' }
              : upload
          ));
        }
      } catch (error) {
        setUploads(prev => prev.map(upload => 
          upload.id === uploadId 
            ? { ...upload, status: 'error', progress: 0, error: 'Status check failed' }
            : upload
        ));
      }
    };

    setTimeout(poll, 5000);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    handleFileSelect(e.dataTransfer.files);
  };

  const removeUpload = (uploadId: string) => {
    setUploads(prev => prev.filter(upload => upload.id !== uploadId));
  };

  const getStatusIcon = (status: UploadStatus['status']) => {
    switch (status) {
      case 'uploading':
        return <Loader2 className="h-4 w-4 animate-spin" />;
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

  const getStatusColor = (status: UploadStatus['status']) => {
    switch (status) {
      case 'uploading':
        return 'bg-blue-100 text-blue-800';
      case 'processing':
        return 'bg-yellow-100 text-yellow-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'error':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-3">
        <Upload className="h-8 w-8 text-blue-600" />
        <div>
          <h1 className="text-2xl font-bold">PDF Upload</h1>
          <p className="text-gray-600">Upload and process PDF documents for AI analysis</p>
        </div>
      </div>

      {/* Upload Area */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Upload PDF Files</CardTitle>
        </CardHeader>
        <CardContent>
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              isDragOver 
                ? 'border-blue-500 bg-blue-50' 
                : 'border-gray-300 hover:border-gray-400'
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <Upload className="h-12 w-12 mx-auto mb-4 text-gray-400" />
            <p className="text-lg font-medium mb-2">
              Drag and drop PDF files here, or click to browse
            </p>
            <p className="text-gray-500 mb-4">
              Supported: PDF files up to 50MB
            </p>
            <Button
              onClick={() => fileInputRef.current?.click()}
              className="flex items-center space-x-2"
            >
              <Download className="h-4 w-4" />
              <span>Choose Files</span>
            </Button>
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept=".pdf"
              onChange={(e) => handleFileSelect(e.target.files)}
              className="hidden"
            />
          </div>
        </CardContent>
      </Card>

      {/* Upload Status */}
      {uploads.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Upload Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {uploads.map((upload) => (
                <div key={upload.id} className="flex items-center space-x-4 p-4 border rounded-lg">
                  <div className="flex-shrink-0">
                    {getStatusIcon(upload.status)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-2">
                      <p className="text-sm font-medium truncate">{upload.filename}</p>
                      <Badge className={getStatusColor(upload.status)}>
                        {upload.status}
                      </Badge>
                    </div>
                    <Progress value={upload.progress} className="h-2 mb-2" />
                    {upload.message && (
                      <p className="text-sm text-gray-600">{upload.message}</p>
                    )}
                    {upload.error && (
                      <p className="text-sm text-red-600">{upload.error}</p>
                    )}
                  </div>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => removeUpload(upload.id)}
                  >
                    <XCircle className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Instructions */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">How it works</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="bg-blue-100 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-3">
                <Upload className="h-6 w-6 text-blue-600" />
              </div>
              <h3 className="font-medium mb-2">1. Upload PDF</h3>
              <p className="text-sm text-gray-600">Drag and drop or select PDF files to upload</p>
            </div>
            <div className="text-center">
              <div className="bg-yellow-100 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-3">
                <Loader2 className="h-6 w-6 text-yellow-600" />
              </div>
              <h3 className="font-medium mb-2">2. AI Processing</h3>
              <p className="text-sm text-gray-600">Our AI extracts text and analyzes content</p>
            </div>
            <div className="text-center">
              <div className="bg-green-100 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-3">
                <CheckCircle className="h-6 w-6 text-green-600" />
              </div>
              <h3 className="font-medium mb-2">3. Ready to Search</h3>
              <p className="text-sm text-gray-600">Search and ask questions about your documents</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default PDFUpload;
