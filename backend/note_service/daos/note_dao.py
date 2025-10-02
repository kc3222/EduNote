from typing import List, Optional
from database import get_db_cursor
from models.models import NoteCreate, NoteUpdate, NoteResponse
import uuid
from datetime import datetime

class NoteDAO:
    """Data Access Object for note operations"""
    
    @staticmethod
    def create(note: NoteCreate) -> NoteResponse:
        """Create a new note"""
        conn, cur = get_db_cursor()
        try:
            note_id = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO note (id, owner_id, document_id, title, markdown, is_archived)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, owner_id, document_id, title, markdown, is_archived, created_at, updated_at
            """, (note_id, note.owner_id, note.document_id, note.title, note.markdown, note.is_archived))
            
            result = cur.fetchone()
            conn.commit()
            return NoteResponse(**dict(result))
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    @staticmethod
    def get_by_id(note_id: str) -> Optional[NoteResponse]:
        """Get a note by ID"""
        conn, cur = get_db_cursor()
        try:
            cur.execute("SELECT * FROM note WHERE id = %s", (note_id,))
            result = cur.fetchone()
            
            if not result:
                return None
            
            return NoteResponse(**dict(result))
        except Exception as e:
            raise e
        finally:
            conn.close()
    
    @staticmethod
    def get_all(owner_id: Optional[str] = None, is_archived: Optional[bool] = None) -> List[NoteResponse]:
        """Get all notes with optional filtering"""
        conn, cur = get_db_cursor()
        try:
            query = "SELECT * FROM note WHERE 1=1"
            params = []
            
            if owner_id:
                query += " AND owner_id = %s"
                params.append(owner_id)
            
            if is_archived is not None:
                query += " AND is_archived = %s"
                params.append(is_archived)
            
            query += " ORDER BY updated_at DESC"
            
            cur.execute(query, params)
            results = cur.fetchall()
            return [NoteResponse(**dict(row)) for row in results]
        except Exception as e:
            raise e
        finally:
            conn.close()
    
    @staticmethod
    def update(note_id: str, note_update: NoteUpdate) -> Optional[NoteResponse]:
        """Update a note"""
        conn, cur = get_db_cursor()
        try:
            # Build dynamic update query
            update_fields = []
            params = []
            
            if note_update.title is not None:
                update_fields.append("title = %s")
                params.append(note_update.title)
            
            if note_update.markdown is not None:
                update_fields.append("markdown = %s")
                params.append(note_update.markdown)
            
            if note_update.document_id is not None:
                update_fields.append("document_id = %s")
                params.append(note_update.document_id)
            
            if note_update.is_archived is not None:
                update_fields.append("is_archived = %s")
                params.append(note_update.is_archived)
            
            if not update_fields:
                raise ValueError("No fields to update")
            
            # Add updated_at
            update_fields.append("updated_at = %s")
            params.append(datetime.now())
            
            # Add note_id for WHERE clause
            params.append(note_id)
            
            query = f"""
                UPDATE note 
                SET {', '.join(update_fields)}
                WHERE id = %s
                RETURNING id, owner_id, document_id, title, markdown, is_archived, created_at, updated_at
            """
            
            cur.execute(query, params)
            result = cur.fetchone()
            
            if not result:
                return None
            
            conn.commit()
            return NoteResponse(**dict(result))
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    @staticmethod
    def delete(note_id: str) -> bool:
        """Delete a note"""
        conn, cur = get_db_cursor()
        try:
            cur.execute("DELETE FROM note WHERE id = %s RETURNING id", (note_id,))
            result = cur.fetchone()
            
            if not result:
                return False
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    @staticmethod
    def get_by_owner(owner_id: str, is_archived: Optional[bool] = None) -> List[NoteResponse]:
        """Get all notes for a specific owner"""
        return NoteDAO.get_all(owner_id=owner_id, is_archived=is_archived)