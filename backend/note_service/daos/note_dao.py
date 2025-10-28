from typing import List, Optional
from note_service.database import get_db_cursor
from note_service.models.models import NoteCreate, NoteUpdate, NoteResponse
import uuid
from datetime import datetime
import json

class NoteDAO:
    """Data Access Object for note operations"""
    
    @staticmethod
    def create(note: NoteCreate) -> NoteResponse:
        """Create a new note"""
        conn, cur = get_db_cursor()
        try:
            note_id = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO note (id, owner_id, document_id, title, markdown, quiz_ids, flashcard_ids, chat_id, is_archived)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, owner_id, document_id, title, markdown, quiz_ids, flashcard_ids, chat_id, is_archived, created_at, updated_at
            """, (note_id, note.owner_id, note.document_id, note.title, note.markdown, 
                  note.quiz_ids, note.flashcard_ids, note.chat_id, note.is_archived))
            
            result = cur.fetchone()
            conn.commit()
            
            # Convert result to dict and parse JSON arrays
            note_dict = dict(result)

            if 'quiz_ids' in note_dict:
                if isinstance(note_dict['quiz_ids'], str):
                    if note_dict['quiz_ids'] == '{}':
                        note_dict['quiz_ids'] = []
                    else:
                        note_dict['quiz_ids'] = json.loads(note_dict['quiz_ids'])
                elif isinstance(note_dict['quiz_ids'], dict):
                    note_dict['quiz_ids'] = []
            if 'flashcard_ids' in note_dict:
                if isinstance(note_dict['flashcard_ids'], str):
                    if note_dict['flashcard_ids'] == '{}':
                        note_dict['flashcard_ids'] = []
                    else:
                        note_dict['flashcard_ids'] = json.loads(note_dict['flashcard_ids'])
                elif isinstance(note_dict['flashcard_ids'], dict):
                    note_dict['flashcard_ids'] = []
            
            print(f"After parsing - quiz_ids: {note_dict.get('quiz_ids')}, flashcard_ids: {note_dict.get('flashcard_ids')}")
            
            return NoteResponse(**note_dict)
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
            
            # Convert result to dict and parse JSON arrays
            note_dict = dict(result)
            
            # Parse quiz_ids
            if 'quiz_ids' in note_dict:
                if isinstance(note_dict['quiz_ids'], str):
                    if note_dict['quiz_ids'] == '{}' or note_dict['quiz_ids'] == '':
                        note_dict['quiz_ids'] = []
                    else:
                        try:
                            note_dict['quiz_ids'] = json.loads(note_dict['quiz_ids'])
                        except json.JSONDecodeError:
                            note_dict['quiz_ids'] = []
                elif isinstance(note_dict['quiz_ids'], dict):
                    note_dict['quiz_ids'] = []
                elif note_dict['quiz_ids'] is None:
                    note_dict['quiz_ids'] = []
            
            # Parse flashcard_ids
            if 'flashcard_ids' in note_dict:
                if isinstance(note_dict['flashcard_ids'], str):
                    if note_dict['flashcard_ids'] == '{}' or note_dict['flashcard_ids'] == '':
                        note_dict['flashcard_ids'] = []
                    else:
                        try:
                            note_dict['flashcard_ids'] = json.loads(note_dict['flashcard_ids'])
                        except json.JSONDecodeError:
                            note_dict['flashcard_ids'] = []
                elif isinstance(note_dict['flashcard_ids'], dict):
                    note_dict['flashcard_ids'] = []
                elif note_dict['flashcard_ids'] is None:
                    note_dict['flashcard_ids'] = []
            
            return NoteResponse(**note_dict)
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
            
            # Convert results to dicts and parse JSON arrays
            notes = []
            for row in results:
                note_dict = dict(row)
                
                # Parse quiz_ids
                if 'quiz_ids' in note_dict:
                    if isinstance(note_dict['quiz_ids'], str):
                        if note_dict['quiz_ids'] == '{}' or note_dict['quiz_ids'] == '':
                            note_dict['quiz_ids'] = []
                        else:
                            try:
                                note_dict['quiz_ids'] = json.loads(note_dict['quiz_ids'])
                            except json.JSONDecodeError:
                                note_dict['quiz_ids'] = []
                    elif isinstance(note_dict['quiz_ids'], dict):
                        note_dict['quiz_ids'] = []
                    elif note_dict['quiz_ids'] is None:
                        note_dict['quiz_ids'] = []
                
                # Parse flashcard_ids
                if 'flashcard_ids' in note_dict:
                    if isinstance(note_dict['flashcard_ids'], str):
                        if note_dict['flashcard_ids'] == '{}' or note_dict['flashcard_ids'] == '':
                            note_dict['flashcard_ids'] = []
                        else:
                            try:
                                note_dict['flashcard_ids'] = json.loads(note_dict['flashcard_ids'])
                            except json.JSONDecodeError:
                                note_dict['flashcard_ids'] = []
                    elif isinstance(note_dict['flashcard_ids'], dict):
                        note_dict['flashcard_ids'] = []
                    elif note_dict['flashcard_ids'] is None:
                        note_dict['flashcard_ids'] = []
                
                notes.append(NoteResponse(**note_dict))
            
            return notes
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
            
            if note_update.quiz_ids is not None:
                update_fields.append("quiz_ids = %s")
                params.append(note_update.quiz_ids)
            
            if note_update.flashcard_ids is not None:
                update_fields.append("flashcard_ids = %s")
                params.append(note_update.flashcard_ids)
            
            if note_update.chat_id is not None:
                update_fields.append("chat_id = %s")
                params.append(note_update.chat_id)
            
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
                RETURNING id, owner_id, document_id, title, markdown, quiz_ids, flashcard_ids, chat_id, is_archived, created_at, updated_at
            """
            
            cur.execute(query, params)
            result = cur.fetchone()
            
            if not result:
                return None
            
            conn.commit()
            
            # Convert result to dict and parse JSON arrays
            note_dict = dict(result)
            if 'quiz_ids' in note_dict:
                if isinstance(note_dict['quiz_ids'], str):
                    if note_dict['quiz_ids'] == '{}':
                        note_dict['quiz_ids'] = []
                    else:
                        note_dict['quiz_ids'] = json.loads(note_dict['quiz_ids'])
                elif isinstance(note_dict['quiz_ids'], dict):
                    note_dict['quiz_ids'] = []
            if 'flashcard_ids' in note_dict:
                if isinstance(note_dict['flashcard_ids'], str):
                    if note_dict['flashcard_ids'] == '{}':
                        note_dict['flashcard_ids'] = []
                    else:
                        note_dict['flashcard_ids'] = json.loads(note_dict['flashcard_ids'])
                elif isinstance(note_dict['flashcard_ids'], dict):
                    note_dict['flashcard_ids'] = []
            
            return NoteResponse(**note_dict)
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
    def get_by_chat(chat_id: str) -> List[NoteResponse]:
        """Get all notes for a specific chat"""
        conn, cur = get_db_cursor()
        try:
            cur.execute("SELECT * FROM note WHERE chat_id = %s ORDER BY created_at ASC", (chat_id,))
            results = cur.fetchall()
            
            # Convert results to dicts and parse JSON arrays
            notes = []
            for row in results:
                note_dict = dict(row)
                if 'quiz_ids' in note_dict and note_dict['quiz_ids']:
                    note_dict['quiz_ids'] = json.loads(note_dict['quiz_ids']) if isinstance(note_dict['quiz_ids'], str) else note_dict['quiz_ids']
                if 'flashcard_ids' in note_dict and note_dict['flashcard_ids']:
                    note_dict['flashcard_ids'] = json.loads(note_dict['flashcard_ids']) if isinstance(note_dict['flashcard_ids'], str) else note_dict['flashcard_ids']
                notes.append(NoteResponse(**note_dict))
            
            return notes
        except Exception as e:
            raise e
        finally:
            conn.close()
    
    @staticmethod
    def get_by_quiz(quiz_id: str) -> List[NoteResponse]:
        """Get all notes that contain a specific quiz"""
        conn, cur = get_db_cursor()
        try:
            cur.execute("SELECT * FROM note WHERE %s = ANY(quiz_ids) ORDER BY created_at ASC", (quiz_id,))
            results = cur.fetchall()
            return [NoteResponse(**dict(row)) for row in results]
        except Exception as e:
            raise e
        finally:
            conn.close()
    
    @staticmethod
    def get_by_flashcard(flashcard_id: str) -> List[NoteResponse]:
        """Get all notes that contain a specific flashcard"""
        conn, cur = get_db_cursor()
        try:
            cur.execute("SELECT * FROM note WHERE %s = ANY(flashcard_ids) ORDER BY created_at ASC", (flashcard_id,))
            results = cur.fetchall()
            return [NoteResponse(**dict(row)) for row in results]
        except Exception as e:
            raise e
        finally:
            conn.close()