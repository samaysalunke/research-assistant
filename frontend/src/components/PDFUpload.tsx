import React, { useState, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Loader2, Upload, FileText, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import { supabase } from '@/services/supabase';
import toast from 'react-hot-toast';

interface UploadStatus {
  id: string;
  filename: string;
  status: 'uploading' | 'processing' | 'completed' | 'failed';
  progress: number;
  error?: string;
}

export default function PDFUpload() {
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploads, setUploads] = useState<UploadStatus[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

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
    
    const files = Array.from(e.dataTransfer.files);
    const pdfFiles = files.filter(file => file.type === 'application/pdf');
    
    if (pdfFiles.length > 0) {
      handleFiles(pdfFiles);
    } else {
      toast.error('Please upload PDF files only');
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    const pdfFiles = files.filter(file => file.type === 'application/pdf');
    
    if (pdfFiles.length > 0) {
      handleFiles(pdfFiles);
    } else {
      toast.error('Please select PDF files only');
    }
  };

  const handleFiles = async (files: File[]) => {
    setIsUploading(true);
    
    for (const file of files) {
      const uploadId = Date.now().toString() + Math.random().toString(36).substr(2, 9);
      
      // Add to uploads list
      setUploads(prev => [...prev, {
        id: uploadId,
        filename: file.name,
        status: 'uploading',
        progress: 0,
      }]);

      try {
        // Upload file
        await uploadPDF(file, uploadId);
      } catch (error) {
        console.error('Upload failed:', error);
        setUploads(prev => prev.map(upload => 
          upload.id === uploadId 
            ? { ...upload, status: 'failed', error: 'Upload failed' }
            : upload
        ));
      }
    }
    
    setIsUploading(false);
  };

  const uploadPDF = async (file: File, uploadId: string) => {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) {
        throw new Error('Not authenticated');
      }

      // Update status to processing
      setUploads(prev => prev.map(upload => 
        upload.id === uploadId 
          ? { ...upload, status: 'processing', progress: 50 }
          : upload
      ));

      // Create FormData
      const formData = new FormData();
      formData.append('file', file);

      // Upload to API
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/ingest/pdf`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Upload failed');
      }

      const result = await response.json();
      
      // Start polling for status
      pollProcessingStatus(result.job_id, uploadId);
      
    } catch (error) {
      console.error('Upload error:', error);
      setUploads(prev => prev.map(upload => 
        upload.id === uploadId 
          ? { ...upload, status: 'failed', error: error instanceof Error ? error.message : 'Upload failed' }
          : upload
      ));
      toast.error(`Failed to upload ${file.name}`);
    }
  };

  const pollProcessingStatus = async (jobId: string, uploadId: string) => {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) return;

      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/ingest/${jobId}/status`, {
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
        },
      });

      if (response.ok) {
        const status = await response.json();
        
        setUploads(prev => prev.map(upload => 
          upload.id === uploadId 
            ? { 
                ...upload, 
                status: status.status === 'completed' ? 'completed' : 'processing',
                progress: status.status === 'completed' ? 100 : 75
              }
            : upload
        ));

        if (status.status === 'completed') {
          toast.success(`Successfully processed ${uploadId}`);
        } else if (status.status === 'failed') {
          setUploads(prev => prev.map(upload => 
            upload.id === uploadId 
              ? { ...upload, status: 'failed', error: status.message || 'Processing failed' }
              : upload
          ));
          toast.error(`Failed to process ${uploadId}`);
        } else {
          // Continue polling
          setTimeout(() => pollProcessingStatus(jobId, uploadId), 2000);
        }
      }
    } catch (error) {
      console.error('Status polling error:', error);
      setUploads(prev => prev.map(upload => 
        upload.id === uploadId 
          ? { ...upload, status: 'failed', error: 'Status check failed' }
          : upload
      ));
    }
  };

  const getStatusIcon = (status: UploadStatus['status']) => {
    switch (status) {
      case 'uploading':
        return <Loader2 className="h-4 w-4 animate-spin text-blue-600" />;
      case 'processing':
        return <Loader2 className="h-4 w-4 animate-spin text-yellow-600" />;
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-600" />;
      default:
        return <AlertCircle className="h-4 w-4 text-gray-600" />;
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
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const removeUpload = (uploadId: string) => {
    setUploads(prev => prev.filter(upload => upload.id !== uploadId));
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-3">
        <FileText className="h-8 w-8 text-purple-600" />
        <div>
          <h1 className="text-2xl font-bold">PDF Upload</h1>
          <p className="text-gray-600">Upload PDF documents for AI processing and analysis</p>
        </div>
      </div>

      {/* Upload Area */}
      <Card>
        <CardHeader>
          <CardTitle>Upload PDF Documents</CardTitle>
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
            <p className="text-lg font-medium mb-2">Drop PDF files here</p>
            <p className="text-gray-600 mb-4">or click to browse</p>
            <Button
              onClick={() => fileInputRef.current?.click()}
              disabled={isUploading}
              className="flex items-center space-x-2"
            >
              <FileText className="h-4 w-4" />
              <span>Select PDF Files</span>
            </Button>
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept=".pdf"
              onChange={handleFileSelect}
              className="hidden"
            />
            <p className="text-sm text-gray-500 mt-4">
              Maximum file size: 50MB per file
            </p>
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
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-3">
                      {getStatusIcon(upload.status)}
                      <span className="font-medium">{upload.filename}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge className={getStatusColor(upload.status)}>
                        {upload.status}
                      </Badge>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => removeUpload(upload.id)}
                        className="h-6 w-6 p-0"
                      >
                        <XCircle className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                  
                  <Progress value={upload.progress} className="mb-2" />
                  
                  {upload.error && (
                    <p className="text-sm text-red-600 mt-2">{upload.error}</p>
                  )}
                  
                  <p className="text-sm text-gray-500">
                    {upload.progress}% complete
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Instructions */}
      <Card>
        <CardHeader>
          <CardTitle>How it works</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="bg-blue-100 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-3">
                <Upload className="h-6 w-6 text-blue-600" />
              </div>
              <h3 className="font-medium mb-2">1. Upload PDF</h3>
              <p className="text-sm text-gray-600">
                Drag and drop or select PDF files from your computer
              </p>
            </div>
            <div className="text-center">
              <div className="bg-yellow-100 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-3">
                <Loader2 className="h-6 w-6 text-yellow-600" />
              </div>
              <h3 className="font-medium mb-2">2. AI Processing</h3>
              <p className="text-sm text-gray-600">
                Our AI extracts text, analyzes content, and generates insights
              </p>
            </div>
            <div className="text-center">
              <div className="bg-green-100 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-3">
                <CheckCircle className="h-6 w-6 text-green-600" />
              </div>
              <h3 className="font-medium mb-2">3. Ready to Search</h3>
              <p className="text-sm text-gray-600">
                Your PDF content is now searchable and available for conversations
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
