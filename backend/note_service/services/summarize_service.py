from typing import Any, Dict, Optional

from note_service.services.ai_service import AIService
from note_service.services.typing_helpers import SummaryDict
from note_service.models.models import NoteResponse


_JSON_SCHEMA_HINT: Dict[str, Any] = {
    "type": "object",
    "required": ["title", "tldr", "key_points"],
    "properties": {
        "title": {
            "type": "string",
            "description": "Short human-readable title for the note",
        },
        "tldr": {
            "type": "string",
            "description": "One-paragraph summary (<= 3 sentences)",
        },
        "key_points": {
            "type": "array",
            "items": {"type": "string"},
            "description": "3-7 bullet points with the most important ideas",
        },
        "action_items": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Explicit action items with verbs",
        },
        "questions": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Open questions / follow-ups",
        },
        "keywords": {
            "type": "array",
            "items": {"type": "string"},
            "description": "5-12 topic keywords",
        },
    },
    "additionalProperties": False,
}


class SummarizeService:
    """
    Note-specific summarization service.

    - Uses AIService/Gemini under the hood.
    - Knows how to build the prompt and normalize the JSON.
    - Optionally persists the summary back to the 'note' table.
    """

    def __init__(self, ai: Optional[AIService] = None) -> None:
        self.ai = ai or AIService()

    def summarize_note(self, note: NoteResponse) -> SummaryDict:
        """
        Build a structured summary for a NoteResponse (no persistence).
        """
        title_hint = (note.title or "").strip()
        body = (note.markdown or "").strip()

        prompt = f"""
            You will receive note content (Markdown). Create a structured summary JSON with keys:
            - "title" (string)
            - "tldr" (string, <= 3 sentences)
            - "key_points" (array of strings, 3-7 bullets, concise)
            - "action_items" (array of strings)
            - "questions" (array of strings)
            - "keywords" (array of strings, 5-12 items)

            IMPORTANT:
            - Output MUST be valid JSON and contain only the JSON object—no additional text.
            - Keep wording concise, professional, and faithful to the note.
            - If the note is empty, return neutral placeholders.

            Title hint (optional): {title_hint!r}

            Note (Markdown) begins:
            ---
            {body[:12000]}
            ---
        """

        data = self.ai.generate_json(
            prompt,
            schema_hint=_JSON_SCHEMA_HINT,
            temperature=0.2,
        )
        return _normalize_summary_dict(data)

    def summarize_and_persist(self, note_id: str) -> SummaryDict:
        """
        Compute summary for note_id and persist to DB (summary_json + summary_updated_at).
        Returns the structured summary dict.

        - Uses NoteService for fetching.
        - Uses DAO helper if available, otherwise falls back to direct SQL UPDATE.
        """
        from note_service.services.note_service import NoteService  # local import to avoid cycles
        import json

        svc = NoteService()
        note = svc.get_note(note_id)
        if not note:
            raise ValueError(f"Note {note_id} not found")

        summary = self.summarize_note(note)

        # Preferred path: use DAO helper if present
        if hasattr(svc, "dao") and hasattr(svc.dao, "update_summary"):
            svc.dao.update_summary(note_id, json.dumps(summary))
        else:
            # Fallback: direct SQL UPDATE
            # IMPORTANT: adjust this import to your actual DB helper module.
            # If your DB helper is `note_service.database`, change accordingly.
            from note_service.db import get_db_cursor  # type: ignore

            conn, cur = get_db_cursor()
            try:
                # If using PostgreSQL and summary_json is jsonb:
                cur.execute(
                    """
                    UPDATE note
                       SET summary_json = %s::jsonb,
                           summary_updated_at = NOW()
                     WHERE id = %s
                    """,
                    (json.dumps(summary), note_id),
                )
                conn.commit()
            finally:
                cur.close()
                conn.close()

        return summary


def _normalize_summary_dict(d: Dict[str, Any]) -> SummaryDict:
    """
    Normalize the raw dict from the LLM into a strongly-typed SummaryDict
    with default values and list coercion.
    """
    title = d.get("title") or ""
    tldr = d.get("tldr") or ""
    key_points = d.get("key_points") or []
    action_items = d.get("action_items") or []
    questions = d.get("questions") or []
    keywords = d.get("keywords") or []

    def _as_list(x: Any) -> list:
        return x if isinstance(x, list) else []

    return {
        "title": str(title),
        "tldr": str(tldr),
        "key_points": [str(x) for x in _as_list(key_points)],
        "action_items": [str(x) for x in _as_list(action_items)],
        "questions": [str(x) for x in _as_list(questions)],
        "keywords": [str(x) for x in _as_list(keywords)],
    }