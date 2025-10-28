from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import List, Optional
import uvicorn
import argparse
import os
import uuid
import shutil
from pathlib import Path
import mimetypes
from datetime import datetime
import json

from document_service.models import DocumentResponse, DocumentCreate
from document_service.services.document_service import DocumentService

app = FastAPI(title="Document Service", version="1.0.0")

# Initialize service
document_service = DocumentService()

FRONTEND_ORIGIN = "http://localhost:5173"

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.get("/")
async def root():
    return {"message": "Document Service is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/documents/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    owner_id: str = Form(...),
    description: Optional[str] = Form(None)
):
    """Upload a document file and create a database record"""
    try:
        # Validate file type
        allowed_types = {
            'application/pdf': '.pdf',
            'text/plain': '.txt',
            'application/msword': '.doc',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
            'text/markdown': '.md'
        }
        
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail=f"File type not supported. Allowed types: {', '.join(allowed_types.values())}"
            )
        
        # Generate unique filename
        file_extension = allowed_types[file.content_type]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = UPLOAD_DIR / unique_filename
        
        # Save file to disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Create document record
        document_data = DocumentCreate(
            title=title or file.filename or "Untitled Document",
            filename=file.filename or "unknown",
            file_path=str(file_path),
            file_size=file_size,
            content_type=file.content_type,
            owner_id=owner_id,
            description=description
        )
        
        return document_service.create_document(document_data)
        
    except Exception as e:
        # Clean up file if database operation fails
        if 'file_path' in locals() and file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents", response_model=List[DocumentResponse])
async def get_documents(owner_id: Optional[str] = None):
    """Get documents with optional filtering by owner"""
    return document_service.get_documents(owner_id=owner_id)

@app.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str):
    """Get a specific document by ID"""
    return document_service.get_document(document_id)

@app.get("/documents/{document_id}/download")
async def download_document(document_id: str):
    """Download a document file"""
    document = document_service.get_document(document_id)
    
    if not os.path.exists(document.file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    return FileResponse(
        path=document.file_path,
        filename=document.filename,
        media_type=document.content_type
    )

@app.get("/documents/{document_id}/view")
async def view_document(document_id: str):
    """View a document file in browser (for PDFs, images, etc.)"""
    document = document_service.get_document(document_id)
    
    if not os.path.exists(document.file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    return FileResponse(
        path=document.file_path,
        media_type=document.content_type,
        headers={"Content-Disposition": "inline"}
    )

@app.put("/documents/{document_id}", response_model=DocumentResponse)
async def update_document(document_id: str, title: Optional[str] = None, description: Optional[str] = None):
    """Update document metadata"""
    return document_service.update_document(document_id, title=title, description=description)

@app.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document and its file"""
    document = document_service.get_document(document_id)
    
    # Delete file from disk
    if os.path.exists(document.file_path):
        os.remove(document.file_path)
    
    return document_service.delete_document(document_id)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Document Service")
    parser.add_argument("--port", type=int, default=8002, help="Port number to run the service on")
    args = parser.parse_args()
    
    print(f"Starting Document Service on port {args.port}")
    uvicorn.run(app, host="0.0.0.0", port=args.port)
