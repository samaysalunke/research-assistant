import React, { useState, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { 
  Upload, 
  FileText, 
  CheckCircle, 
  XCircle, 
  AlertCircle,
  Loader2
} from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';

interface UploadStatus {
  id: string;
  filename: string;
  status: 'uploading' | 'processing' | 'completed' | 'error';
  progress: number;
  message?: string;
  error?: string;
}

const PDFUpload: React.FC = () => {
  const { session } = useAuth();
  const [uploads, setUploads] = useState<UploadStatus[]>([]);
  const [isDragging, setIsDragging] = useState(false);
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
    
    // Add to uploads list
    setUploads(prev => [...prev, {
      id: uploadId,
      filename: file.name,
      status: 'uploading',
      progress: 0
    }]);

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
            ? { 
                ...upload, 
                status: 'processing', 
                progress: 50,
                message: result.message || 'Processing started'
              }
            : upload
        ));

        // Simulate processing progress
        const progressInterval = setInterval(() => {
          setUploads(prev => prev.map(upload => {
            if (upload.id === uploadId && upload.status === 'processing') {
              const newProgress = Math.min(upload.progress + 10, 90);
              return { ...upload, progress: newProgress };
            }
            return upload;
          }));
        }, 1000);

        // Check processing status
        const checkStatus = async () => {
          try {
            const statusResponse = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/ingest/status/${result.job_id}`, {
              headers: {
                'Authorization': `Bearer ${localStorage.getItem('supabase.auth.token')}`,
              },
            });

            if (statusResponse.ok) {
              const statusData = await statusResponse.json();
              
              if (statusData.status === 'completed') {
                clearInterval(progressInterval);
                setUploads(prev => prev.map(upload => 
                  upload.id === uploadId 
                    ? { 
                        ...upload, 
                        status: 'completed', 
                        progress: 100,
                        message: 'Processing completed successfully'
                      }
                    : upload
                ));
              } else if (statusData.status === 'failed') {
                clearInterval(progressInterval);
                setUploads(prev => prev.map(upload => 
                  upload.id === uploadId 
                    ? { 
                        ...upload, 
                        status: 'error', 
                        error: statusData.error || 'Processing failed'
                      }
                    : upload
                ));
              }
            }
          } catch (error) {
            console.error('Status check failed:', error);
          }
        };

        // Check status every 5 seconds
        const statusInterval = setInterval(checkStatus, 5000);
        
        // Stop checking after 2 minutes
        setTimeout(() => {
          clearInterval(statusInterval);
          clearInterval(progressInterval);
        }, 120000);

      } else {
        throw new Error('Upload failed');
      }
    } catch (error) {
      console.error('Upload error:', error);
      setUploads(prev => prev.map(upload => 
        upload.id === uploadId 
          ? { 
              ...upload, 
              status: 'error', 
              error: 'Upload failed'
            }
          : upload
      ));
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    handleFileSelect(e.dataTransfer.files);
  };

  const removeUpload = (uploadId: string) => {
    setUploads(prev => prev.filter(upload => upload.id !== uploadId));
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'uploading':
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

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'processing':
        return 'bg-yellow-100 text-yellow-800';
      case 'error':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-blue-100 text-blue-800';
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-3">
        <Upload className="h-8 w-8 text-blue-600" />
        <div>
          <h1 className="text-2xl font-bold">PDF Upload</h1>
          <p className="text-gray-600">Upload and process PDF documents</p>
        </div>
      </div>

      {/* Upload Area */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <FileText className="h-5 w-5" />
            <span>Upload PDF Files</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              isDragging 
                ? 'border-blue-500 bg-blue-50' 
                : 'border-gray-300 hover:border-gray-400'
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <Upload className="h-12 w-12 mx-auto mb-4 text-gray-400" />
            <p className="text-lg font-medium text-gray-900 mb-2">
              Drop PDF files here or click to browse
            </p>
            <p className="text-gray-500 mb-4">
              Supported format: PDF only
            </p>
            <Button
              onClick={() => fileInputRef.current?.click()}
              className="flex items-center space-x-2"
            >
              <Upload className="h-4 w-4" />
              <span>Choose Files</span>
            </Button>
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf"
              multiple
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
            <CardTitle>Upload Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {uploads.map((upload) => (
                <div key={upload.id} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-3">
                      {getStatusIcon(upload.status)}
                      <div>
                        <p className="font-medium">{upload.filename}</p>
                        {upload.message && (
                          <p className="text-sm text-gray-600">{upload.message}</p>
                        )}
                        {upload.error && (
                          <p className="text-sm text-red-600">{upload.error}</p>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge className={getStatusColor(upload.status)}>
                        {upload.status}
                      </Badge>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => removeUpload(upload.id)}
                      >
                        <XCircle className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                  
                  {(upload.status === 'uploading' || upload.status === 'processing') && (
                    <Progress value={upload.progress} className="h-2" />
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Instructions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <AlertCircle className="h-5 w-5" />
            <span>Instructions</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3 text-sm text-gray-600">
            <p>• Upload PDF files by dragging and dropping or clicking the upload button</p>
            <p>• Files will be automatically processed and added to your library</p>
            <p>• Processing time depends on file size and content complexity</p>
            <p>• You can track the progress of each upload in real-time</p>
            <p>• Once processed, documents will be searchable and available for AI chat</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default PDFUpload;
