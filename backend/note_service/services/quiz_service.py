from typing import Any, Dict, Optional
import json

from note_service.AI.gemini_client import GeminiClient
from note_service.models.models import NoteResponse


_QUIZ_SCHEMA_HINT: Dict[str, Any] = {
    "type": "object",
    "required": ["title", "questions"],
    "properties": {
        "title": {
            "type": "string",
            "description": "Short human-readable title for the quiz",
        },
        "questions": {
            "type": "array",
            "description": "List of quiz questions",
            "items": {
                "type": "object",
                "required": ["id", "question", "options", "correct_option"],
                "properties": {
                    "id": {"type": "string"},
                    "question": {"type": "string"},
                    "options": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "3–6 answer options",
                    },
                    "correct_option": {
                        "type": "integer",
                        "description": "0-based index into options[]",
                    },
                    "explanation": {
                        "type": "string",
                        "description": "Short explanation of the answer (optional)",
                    },
                    "difficulty": {
                        "type": "string",
                        "description": "e.g. easy, medium, hard (optional)",
                    },
                },
                "additionalProperties": False,
            },
        },
    },
    "additionalProperties": False,
}


class QuizService:
    """
    Generate a quiz from a note using Gemini and store it on the note row.
    """

    def __init__(self, gemini: Optional[GeminiClient] = None) -> None:
        self.gemini = gemini or GeminiClient(model="gemini-2.5-flash")

    def _generate_quiz_for_note(self, note: NoteResponse) -> Dict[str, Any]:
        title_hint = (note.title or "").strip()
        body = (note.markdown or "").strip()

        prompt = f"""
            You will receive note content (Markdown). Create a multiple-choice quiz as a JSON object.

            JSON format:
            {{
              "title": string,
              "questions": [
                {{
                  "id": string,
                  "question": string,
                  "options": [string, ...],    // 3–6 options
                  "correct_option": integer,    // 0-based index into options[]
                  "explanation": string,        // brief explanation (optional)
                  "difficulty": string          // e.g. "easy", "medium", "hard" (optional)
                }},
                ...
              ]
            }}

            IMPORTANT:
            - Output MUST be valid JSON and contain only the JSON object—no extra text.
            - Use 5–10 questions, focusing on key concepts in the note.
            - If the note is very short or empty, still return a small but valid quiz.

            Note title hint: {title_hint!r}

            Note (Markdown) begins:
            ---
            {body[:12000]}
            ---
        """

        data = self.gemini.generate_json(
            prompt,
            schema_hint=_QUIZ_SCHEMA_HINT,
            temperature=0.4,
        )

        # ---- SAFE NORMALIZATION ----
        raw_questions = data.get("questions") or []
        normalized_questions = []

        for idx, raw in enumerate(raw_questions):
            q: Dict[str, Any]

            if isinstance(raw, dict):
                # Already structured
                q = dict(raw)

            elif isinstance(raw, str):
                # Gemini sometimes returns a Python-repr or JSON string for each question.
                s = raw.strip()
                parsed = None

                if s.startswith("{") and s.endswith("}"):
                    # Try JSON first
                    try:
                        parsed = json.loads(s)
                    except json.JSONDecodeError:
                        # Try to convert Python repr → JSON
                        try:
                            fixed = (
                                s.replace("'", '"')
                                 .replace("None", "null")
                                 .replace("True", "true")
                                 .replace("False", "false")
                            )
                            parsed = json.loads(fixed)
                        except json.JSONDecodeError:
                            parsed = None

                if isinstance(parsed, dict):
                    q = parsed
                else:
                    # Fall back to treating it as plain question text
                    q = {
                        "question": s,
                        "options": [],
                        "correct_option": 0,
                    }

            else:
                # Some weird type → stringify
                q = {
                    "question": str(raw),
                    "options": [],
                    "correct_option": 0,
                }

            # Ensure required fields
            q.setdefault("id", f"q_{idx + 1}")

            options = q.get("options") or []
            if not isinstance(options, list):
                options = [str(options)]
            q["options"] = [str(o) for o in options]

            # Normalize correct_option
            try:
                correct_idx = int(q.get("correct_option", 0))
            except (TypeError, ValueError):
                correct_idx = 0

            if not q["options"]:
                correct_idx = 0
            elif correct_idx < 0 or correct_idx >= len(q["options"]):
                correct_idx = 0

            q["correct_option"] = correct_idx

            normalized_questions.append(q)

        data["title"] = str(data.get("title") or (title_hint or "Generated Quiz"))
        data["questions"] = normalized_questions

    def generate_and_persist(self, note_id: str) -> Dict[str, Any]:
        """
        Generate a quiz for note_id and persist it in note.quiz_json + quiz_updated_at.
        Returns the quiz JSON.
        """
        from note_service.services.note_service import NoteService
        from note_service.database import get_db_cursor  # 👈 ensure this import is correct

        svc = NoteService()
        note = svc.get_note(note_id)
        if not note:
            raise ValueError(f"Note {note_id} not found")

        quiz = self._generate_quiz_for_note(note)

        # If DAO has a helper, use it; else, raw SQL.
        if hasattr(svc, "dao") and hasattr(svc.dao, "update_quiz"):
            svc.dao.update_quiz(note_id, json.dumps(quiz))
            return quiz

        conn, cur = get_db_cursor()
        try:
            cur.execute(
                """
                UPDATE note
                   SET quiz_json = %s::jsonb,
                       quiz_updated_at = NOW()
                 WHERE id = %s
                """,
                (json.dumps(quiz), note_id),
            )
            conn.commit()
        finally:
            cur.close()
            conn.close()

        return quiz