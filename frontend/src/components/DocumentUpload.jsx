import React, { useState, useRef } from 'react';
import { Upload, File, X, Check, AlertCircle, FileText, Image } from 'lucide-react';

export default function DocumentUpload({ user, onUploadComplete, onClose }) {
  const [isDragging, setIsDragging] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef(null);

  const allowedTypes = {
    'application/pdf': { icon: FileText, color: 'text-red-500', bg: 'bg-red-50' },
    'text/plain': { icon: FileText, color: 'text-gray-500', bg: 'bg-gray-50' },
    'application/msword': { icon: FileText, color: 'text-blue-500', bg: 'bg-blue-50' },
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': { icon: FileText, color: 'text-blue-500', bg: 'bg-blue-50' },
    'text/markdown': { icon: FileText, color: 'text-purple-500', bg: 'bg-purple-50' }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
  };

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files);
    handleFiles(files);
  };

  const handleFiles = (files) => {
    const validFiles = files.filter(file => {
      if (!allowedTypes[file.type]) {
        alert(`File type ${file.type} is not supported`);
        return false;
      }
      if (file.size > 50 * 1024 * 1024) { // 50MB limit
        alert(`File ${file.name} is too large. Maximum size is 50MB.`);
        return false;
      }
      return true;
    });

    const newFiles = validFiles.map(file => ({
      file,
      id: Date.now() + Math.random(),
      status: 'pending',
      progress: 0,
      title: file.name.replace(/\.[^/.]+$/, ""), // Remove extension for default title
      description: ''
    }));

    setUploadedFiles(prev => [...prev, ...newFiles]);
  };

  const removeFile = (fileId) => {
    setUploadedFiles(prev => prev.filter(f => f.id !== fileId));
  };

  const updateFileMetadata = (fileId, field, value) => {
    setUploadedFiles(prev => prev.map(f => 
      f.id === fileId ? { ...f, [field]: value } : f
    ));
  };

  const uploadFiles = async () => {
    setUploading(true);
    const pendingFiles = uploadedFiles.filter(f => f.status === 'pending');
    const successfulUploads = []; // Track successful uploads
    
    for (const fileItem of pendingFiles) {
      try {
        // Update status to uploading
        setUploadedFiles(prev => prev.map(f => 
          f.id === fileItem.id ? { ...f, status: 'uploading', progress: 0 } : f
        ));

        const formData = new FormData();
        formData.append('file', fileItem.file);
        formData.append('title', fileItem.title);
        formData.append('owner_id', user.id);
        if (fileItem.description) {
          formData.append('description', fileItem.description);
        }

        const response = await fetch('/documents/upload', {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          const error = await response.json();
          throw new Error(error.detail || 'Upload failed');
        }

        const result = await response.json();
        console.log("Upload successful, response:", result);
        
        // Update status to success
        setUploadedFiles(prev => prev.map(f => 
          f.id === fileItem.id ? { ...f, status: 'success', progress: 100, documentId: result.id } : f
        ));

        // Add to successful uploads array
        successfulUploads.push({
          ...fileItem,
          documentId: result.id,
          status: 'success'
        });

      } catch (error) {
        console.error('Upload error:', error);
        setUploadedFiles(prev => prev.map(f => 
          f.id === fileItem.id ? { ...f, status: 'error', error: error.message } : f
        ));
      }
    }

    setUploading(false);
    
    // Call onUploadComplete with actual successful uploads
    console.log("Upload process complete. Successful uploads:", successfulUploads);
    if (onUploadComplete && successfulUploads.length > 0) {
      console.log("Calling onUploadComplete with:", successfulUploads);
      onUploadComplete(successfulUploads);
    } else {
      console.log("Not calling onUploadComplete - no successful uploads or no callback");
    }
  };

  const getFileIcon = (file) => {
    const typeInfo = allowedTypes[file.type];
    const IconComponent = typeInfo?.icon || File;
    return <IconComponent className={`h-6 w-6 ${typeInfo?.color || 'text-gray-500'}`} />;
  };

  const getFileTypeLabel = (type) => {
    const labels = {
      'application/pdf': 'PDF',
      'text/plain': 'Text',
      'application/msword': 'Word Doc',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'Word Doc',
      'text/markdown': 'Markdown'
    };
    return labels[type] || 'Unknown';
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Upload className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-900">Upload Documents</h2>
              <p className="text-sm text-gray-500">Drag and drop files or click to browse</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="h-5 w-5 text-gray-500" />
          </button>
        </div>

        {/* Upload Area */}
        <div className="p-6">
          <div
            className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors ${
              isDragging 
                ? 'border-blue-400 bg-blue-50' 
                : 'border-gray-300 hover:border-gray-400'
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <Upload className={`h-12 w-12 mx-auto mb-4 ${isDragging ? 'text-blue-500' : 'text-gray-400'}`} />
            <p className="text-lg font-medium text-gray-900 mb-2">
              Drop files here or click to browse
            </p>
            <p className="text-sm text-gray-500 mb-4">
              Supports PDF, Word, Text, and Markdown files (max 50MB each)
            </p>
            <button
              onClick={() => fileInputRef.current?.click()}
              className="inline-flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Upload className="h-4 w-4" />
              Choose Files
            </button>
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept=".pdf,.txt,.doc,.docx,.md"
              onChange={handleFileSelect}
              className="hidden"
            />
          </div>

          {/* File List */}
          {uploadedFiles.length > 0 && (
            <div className="mt-6 max-h-64 overflow-y-auto">
              <h3 className="text-sm font-medium text-gray-900 mb-3">Files to Upload</h3>
              <div className="space-y-3">
                {uploadedFiles.map((fileItem) => (
                  <div key={fileItem.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-start gap-3">
                      <div className="flex-shrink-0">
                        {getFileIcon(fileItem.file)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-medium text-gray-900 truncate">
                              {fileItem.file.name}
                            </span>
                            <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                              {getFileTypeLabel(fileItem.file.type)}
                            </span>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="text-xs text-gray-500">
                              {formatFileSize(fileItem.file.size)}
                            </span>
                            {fileItem.status === 'pending' && (
                              <button
                                onClick={() => removeFile(fileItem.id)}
                                className="p-1 hover:bg-gray-100 rounded"
                              >
                                <X className="h-4 w-4 text-gray-400" />
                              </button>
                            )}
                            {fileItem.status === 'success' && (
                              <Check className="h-4 w-4 text-green-500" />
                            )}
                            {fileItem.status === 'error' && (
                              <AlertCircle className="h-4 w-4 text-red-500" />
                            )}
                          </div>
                        </div>
                        
                        {/* Title Input */}
                        <input
                          type="text"
                          placeholder="Document title"
                          value={fileItem.title}
                          onChange={(e) => updateFileMetadata(fileItem.id, 'title', e.target.value)}
                          disabled={fileItem.status !== 'pending'}
                          className="w-full text-sm border border-gray-300 rounded px-3 py-1 mb-2 disabled:bg-gray-100"
                        />
                        
                        {/* Description Input */}
                        <input
                          type="text"
                          placeholder="Description (optional)"
                          value={fileItem.description}
                          onChange={(e) => updateFileMetadata(fileItem.id, 'description', e.target.value)}
                          disabled={fileItem.status !== 'pending'}
                          className="w-full text-sm border border-gray-300 rounded px-3 py-1 disabled:bg-gray-100"
                        />
                        
                        {/* Status Messages */}
                        {fileItem.status === 'uploading' && (
                          <div className="mt-2">
                            <div className="flex items-center gap-2 text-sm text-blue-600">
                              <div className="animate-spin h-4 w-4 border-2 border-blue-600 border-t-transparent rounded-full"></div>
                              Uploading...
                            </div>
                          </div>
                        )}
                        {fileItem.status === 'error' && (
                          <div className="mt-2 text-sm text-red-600">
                            Error: {fileItem.error}
                          </div>
                        )}
                        {fileItem.status === 'success' && (
                          <div className="mt-2 text-sm text-green-600">
                            Upload successful!
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Actions */}
          {uploadedFiles.length > 0 && (
            <div className="mt-6 flex items-center justify-between">
              <div className="text-sm text-gray-500">
                {uploadedFiles.length} file{uploadedFiles.length !== 1 ? 's' : ''} ready
              </div>
              <div className="flex gap-3">
                <button
                  onClick={() => setUploadedFiles([])}
                  disabled={uploading}
                  className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 disabled:opacity-50"
                >
                  Clear All
                </button>
                <button
                  onClick={uploadFiles}
                  disabled={uploading || uploadedFiles.filter(f => f.status === 'pending').length === 0}
                  className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {uploading ? 'Uploading...' : 'Upload Files'}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
