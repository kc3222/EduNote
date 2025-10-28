import uuid
from typing import List, Optional
from document_service.models import DocumentCreate, DocumentResponse
from document_service.database import get_db_connection
import psycopg2
from datetime import datetime

class DocumentService:
    def create_document(self, document: DocumentCreate) -> DocumentResponse:
        """Create a new document record"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                document_id = str(uuid.uuid4())
                cursor.execute("""
                    INSERT INTO document (id, title, filename, file_path, file_size, content_type, owner_id, description)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id, title, filename, file_size, content_type, owner_id, description, created_at, updated_at
                """, (
                    document_id,
                    document.title,
                    document.filename,
                    document.file_path,
                    document.file_size,
                    document.content_type,
                    document.owner_id,
                    document.description
                ))
                
                result = cursor.fetchone()
                conn.commit()
                
                return DocumentResponse(
                    id=result[0],
                    title=result[1],
                    filename=result[2],
                    file_size=result[3],
                    content_type=result[4],
                    owner_id=result[5],
                    description=result[6],
                    created_at=result[7],
                    updated_at=result[8]
                )
        except Exception as e:
            conn.rollback()
            raise Exception(f"Failed to create document: {str(e)}")
        finally:
            conn.close()

    def get_documents(self, owner_id: Optional[str] = None) -> List[DocumentResponse]:
        """Get all documents, optionally filtered by owner"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                if owner_id:
                    cursor.execute("""
                        SELECT id, title, filename, file_size, content_type, owner_id, description, created_at, updated_at
                        FROM document 
                        WHERE owner_id = %s
                        ORDER BY created_at DESC
                    """, (owner_id,))
                else:
                    cursor.execute("""
                        SELECT id, title, filename, file_size, content_type, owner_id, description, created_at, updated_at
                        FROM document 
                        ORDER BY created_at DESC
                    """)
                
                results = cursor.fetchall()
                
                return [
                    DocumentResponse(
                        id=row[0],
                        title=row[1],
                        filename=row[2],
                        file_size=row[3],
                        content_type=row[4],
                        owner_id=row[5],
                        description=row[6],
                        created_at=row[7],
                        updated_at=row[8]
                    )
                    for row in results
                ]
        except Exception as e:
            raise Exception(f"Failed to get documents: {str(e)}")
        finally:
            conn.close()

    def get_document(self, document_id: str) -> DocumentResponse:
        """Get a specific document by ID"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, title, filename, file_path, file_size, content_type, owner_id, description, created_at, updated_at
                    FROM document 
                    WHERE id = %s
                """, (document_id,))
                
                result = cursor.fetchone()
                if not result:
                    raise Exception("Document not found")
                
                # Store file_path for internal use but don't expose in response
                return type('DocumentWithPath', (), {
                    'id': result[0],
                    'title': result[1],
                    'filename': result[2],
                    'file_path': result[3],  # For internal use
                    'file_size': result[4],
                    'content_type': result[5],
                    'owner_id': result[6],
                    'description': result[7],
                    'created_at': result[8],
                    'updated_at': result[9]
                })()
        except Exception as e:
            raise Exception(f"Failed to get document: {str(e)}")
        finally:
            conn.close()

    def update_document(self, document_id: str, title: Optional[str] = None, description: Optional[str] = None) -> DocumentResponse:
        """Update document metadata"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # Build dynamic update query
                updates = []
                params = []
                
                if title is not None:
                    updates.append("title = %s")
                    params.append(title)
                
                if description is not None:
                    updates.append("description = %s")
                    params.append(description)
                
                if not updates:
                    # No updates to make, just return current document
                    return self.get_document(document_id)
                
                # Add updated_at
                updates.append("updated_at = NOW()")
                params.append(document_id)
                
                query = f"""
                    UPDATE document 
                    SET {', '.join(updates)}
                    WHERE id = %s
                    RETURNING id, title, filename, file_size, content_type, owner_id, description, created_at, updated_at
                """
                
                cursor.execute(query, params)
                result = cursor.fetchone()
                
                if not result:
                    raise Exception("Document not found")
                
                conn.commit()
                
                return DocumentResponse(
                    id=result[0],
                    title=result[1],
                    filename=result[2],
                    file_size=result[3],
                    content_type=result[4],
                    owner_id=result[5],
                    description=result[6],
                    created_at=result[7],
                    updated_at=result[8]
                )
        except Exception as e:
            conn.rollback()
            raise Exception(f"Failed to update document: {str(e)}")
        finally:
            conn.close()

    def delete_document(self, document_id: str) -> dict:
        """Delete a document"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM document WHERE id = %s", (document_id,))
                
                if cursor.rowcount == 0:
                    raise Exception("Document not found")
                
                conn.commit()
                return {"message": "Document deleted successfully"}
        except Exception as e:
            conn.rollback()
            raise Exception(f"Failed to delete document: {str(e)}")
        finally:
            conn.close()
