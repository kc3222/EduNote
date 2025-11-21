from typing import List, Optional
from note_service.database import get_db_cursor
from note_service.models.models import NoteCreate, NoteUpdate, NoteResponse
import uuid
from datetime import datetime
import json
from typing import Any, Dict, List

def _row_to_dict(cur, row) -> Dict[str, Any]:
    """
    Convert a DB row to a dict regardless of cursor factory.
    Works with tuple rows (default cursor) or dict-like rows (RealDictCursor).
    """
    if isinstance(row, dict):
        return dict(row)

    # Fallback for tuple rows
    cols = []
    for d in cur.description:
        # psycopg2: d can be a sequence or an object with .name
        if hasattr(d, "name"):
            cols.append(d.name)
        else:
            cols.append(d[0])
    return dict(zip(cols, row))


def _to_list(val) -> List[str]:
    """
    Normalize a DB column that may be ARRAY, JSONB, text JSON, or None to a list[str].
    """
    if val is None:
        return []
    if isinstance(val, list):
        return val
    if isinstance(val, tuple):
        return list(val)
    if isinstance(val, str):
        # try to parse JSON text like '["a","b"]'
        try:
            parsed = json.loads(val)
            if isinstance(parsed, list):
                return parsed
        except Exception:
            # treat as single string element
            return [val]
    return [str(val)]

class NoteDAO:
    """Data Access Object for note operations"""
    
    @staticmethod
    def create(note: NoteCreate) -> NoteResponse:
        """Create a new note"""
        conn, cur = get_db_cursor()
        try:
            note_id = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO note (id, owner_id, document_id, title, markdown, quiz_ids, flashcard_ids, chat_id, is_archived, font_size, font_family, line_height)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, owner_id, document_id, title, markdown, quiz_ids, flashcard_ids, chat_id, is_archived, created_at, updated_at, summary_json, summary_updated_at, font_size, font_family, line_height
            """, (note_id, note.owner_id, note.document_id, note.title, note.markdown, 
                  note.quiz_ids, note.flashcard_ids, note.chat_id, note.is_archived, note.font_size, note.font_family, note.line_height))
            
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
            
            if note_update.font_size is not None:
                update_fields.append("font_size = %s")
                params.append(note_update.font_size)
            
            if note_update.font_family is not None:
                update_fields.append("font_family = %s")
                params.append(note_update.font_family)
            
            if note_update.line_height is not None:
                update_fields.append("line_height = %s")
                params.append(note_update.line_height)
            
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
                RETURNING id, owner_id, document_id, title, markdown, quiz_ids, flashcard_ids, chat_id, is_archived, created_at, updated_at, summary_json, summary_updated_at, font_size, font_family, line_height
            """
            
            cur.execute(query, params)
            result = cur.fetchone()
            
            if not result:
                return None
            
            conn.commit()
            
            # Convert result to dict and handle arrays
            note_dict = dict(result)
            
            # Handle arrays
            if 'quiz_ids' in note_dict:
                if isinstance(note_dict['quiz_ids'], str):
                    if note_dict['quiz_ids'] == '{}':
                        note_dict['quiz_ids'] = []
                    else:
                        try:
                            note_dict['quiz_ids'] = json.loads(note_dict['quiz_ids'])
                        except:
                            note_dict['quiz_ids'] = []
                elif isinstance(note_dict['quiz_ids'], dict):
                    note_dict['quiz_ids'] = []
                elif note_dict['quiz_ids'] is None:
                    note_dict['quiz_ids'] = []
                # If it's already a list, keep it as is
            else:
                note_dict['quiz_ids'] = []
                
            if 'flashcard_ids' in note_dict:
                if isinstance(note_dict['flashcard_ids'], str):
                    if note_dict['flashcard_ids'] == '{}':
                        note_dict['flashcard_ids'] = []
                    else:
                        try:
                            note_dict['flashcard_ids'] = json.loads(note_dict['flashcard_ids'])
                        except:
                            note_dict['flashcard_ids'] = []
                elif isinstance(note_dict['flashcard_ids'], dict):
                    note_dict['flashcard_ids'] = []
                elif note_dict['flashcard_ids'] is None:
                    note_dict['flashcard_ids'] = []
                # If it's already a list, keep it as is
            else:
                note_dict['flashcard_ids'] = []
            
            # Add default values for summary columns (in case they don't exist in DB)
            if 'summary_json' not in note_dict:
                note_dict['summary_json'] = None
            elif isinstance(note_dict['summary_json'], str):
                try:
                    note_dict['summary_json'] = json.loads(note_dict['summary_json'])
                except:
                    note_dict['summary_json'] = None
            
            if 'summary_updated_at' not in note_dict:
                note_dict['summary_updated_at'] = None
            
            # Ensure markdown is not None if required
            if 'markdown' not in note_dict or note_dict['markdown'] is None:
                note_dict['markdown'] = ''
            
            try:
                return NoteResponse(**note_dict)
            except Exception as e:
                raise e
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

    def get_note(self, note_id: str) -> Dict[str, Any] | None:
        conn, cur = get_db_cursor()
        try:
            cur.execute(
                """
                SELECT
                    id, owner_id, title, markdown, document_id,
                    quiz_ids, flashcard_ids, chat_id, is_archived,
                    created_at, updated_at,
                    summary_json, summary_updated_at,
                    font_size, font_family, line_height
                FROM note
                WHERE id = %s
                """,
                (note_id,),
            )
            row = cur.fetchone()
            if not row:
                return None

            rec = _row_to_dict(cur, row)

            # Normalize types
            rec["quiz_ids"] = _to_list(rec.get("quiz_ids"))
            rec["flashcard_ids"] = _to_list(rec.get("flashcard_ids"))

            sj = rec.get("summary_json")
            if isinstance(sj, str):
                try:
                    rec["summary_json"] = json.loads(sj)
                except Exception:
                    rec["summary_json"] = None

            # Booleans might be ints in some setups
            rec["is_archived"] = bool(rec.get("is_archived"))

            return rec
        finally:
            cur.close()
            conn.close()

    def get_notes(self, owner_id: str | None = None, is_archived: bool | None = None) -> List[Dict[str, Any]]:
        conn, cur = get_db_cursor()
        try:
            clauses = []
            params: List[Any] = []

            if owner_id:
                clauses.append("owner_id = %s")
                params.append(owner_id)
            if is_archived is not None:
                clauses.append("is_archived = %s")
                params.append(is_archived)

            where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""

            cur.execute(
                f"""
                SELECT
                    id, owner_id, title, markdown, document_id,
                    quiz_ids, flashcard_ids, chat_id, is_archived,
                    created_at, updated_at,
                    summary_json, summary_updated_at,
                    font_size, font_family, line_height
                FROM note
                {where_sql}
                ORDER BY updated_at DESC NULLS LAST, created_at DESC NULLS LAST
                """,
                tuple(params),
            )

            rows = cur.fetchall() or []
            out: List[Dict[str, Any]] = []

            for r in rows:
                rec = _row_to_dict(cur, r)

                rec["quiz_ids"] = _to_list(rec.get("quiz_ids"))
                rec["flashcard_ids"] = _to_list(rec.get("flashcard_ids"))

                sj = rec.get("summary_json")
                if isinstance(sj, str):
                    try:
                        rec["summary_json"] = json.loads(sj)
                    except Exception:
                        rec["summary_json"] = None

                rec["is_archived"] = bool(rec.get("is_archived"))

                out.append(rec)

            return out
        finally:
            cur.close()
            conn.close()

    def update_summary(self, note_id: str, summary_dict: Dict[str, Any]) -> None:
        conn, cur = get_db_cursor()
        try:
            cur.execute(
                """
                UPDATE note
                SET summary_json = %s,
                    summary_updated_at = NOW()
                WHERE id = %s
                """,
                (json.dumps(summary_dict), note_id),
            )
            conn.commit()
        finally:
            cur.close()
            conn.close()