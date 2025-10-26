import React, { useState, useEffect } from 'react';
import { FileText, Download, ExternalLink, AlertCircle, Loader2 } from 'lucide-react';

export default function PDFViewer({ documentId, document, onDocumentSelect }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pdfUrl, setPdfUrl] = useState(null);

  useEffect(() => {
    if (documentId && !document) {
      loadDocument();
    } else if (document) {
      setPdfUrl(`/documents/${document.id}/view`);
    }
  }, [documentId, document]);

  const loadDocument = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`/documents/${documentId}`);
      if (!response.ok) {
        throw new Error('Failed to load document');
      }
      
      const doc = await response.json();
      if (doc.content_type === 'application/pdf') {
        setPdfUrl(`/documents/${documentId}/view`);
      } else {
        setError('Document is not a PDF file');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (document) {
      window.open(`/documents/${document.id}/download`, '_blank');
    } else if (documentId) {
      window.open(`/documents/${documentId}/download`, '_blank');
    }
  };

  const handleOpenInNewTab = () => {
    if (pdfUrl) {
      window.open(pdfUrl, '_blank');
    }
  };

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center bg-gray-50 rounded-xl">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin text-blue-500 mx-auto mb-3" />
          <p className="text-sm text-gray-600">Loading document...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="h-full flex items-center justify-center bg-red-50 rounded-xl">
        <div className="text-center">
          <AlertCircle className="h-8 w-8 text-red-500 mx-auto mb-3" />
          <p className="text-sm text-red-600 mb-2">Error loading document</p>
          <p className="text-xs text-red-500">{error}</p>
        </div>
      </div>
    );
  }

  if (!pdfUrl && !documentId && !document) {
    return (
      <div className="h-full flex items-center justify-center bg-gradient-to-br from-white to-emerald-50 rounded-xl">
        <div className="text-center">
          <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-lg font-medium text-gray-600 mb-2">No document selected</p>
          <p className="text-sm text-gray-500">Upload a PDF to view it here</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-white rounded-xl border border-gray-200">
      {/* PDF Controls */}
      <div className="flex items-center justify-between p-3 border-b border-gray-200 bg-gray-50 rounded-t-xl">
        <div className="flex items-center gap-2 min-w-0 flex-1">
          <FileText className="h-4 w-4 text-red-500 flex-shrink-0" />
          <span className="text-sm font-medium text-gray-700 truncate">
            {document?.title || document?.filename || 'PDF Document'}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleDownload}
            className="p-1.5 hover:bg-gray-200 rounded transition-colors"
            title="Download"
          >
            <Download className="h-4 w-4 text-gray-600" />
          </button>
          <button
            onClick={handleOpenInNewTab}
            className="p-1.5 hover:bg-gray-200 rounded transition-colors"
            title="Open in new tab"
          >
            <ExternalLink className="h-4 w-4 text-gray-600" />
          </button>
        </div>
      </div>

      {/* PDF Viewer */}
      <div className="flex-1 overflow-hidden">
        {pdfUrl ? (
          <iframe
            src={pdfUrl}
            className="w-full h-full border-0"
            title="PDF Viewer"
            loading="lazy"
          />
        ) : (
          <div className="h-full flex items-center justify-center bg-gray-50">
            <div className="text-center">
              <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-sm text-gray-600">Unable to display document</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
