from typing import Any, Dict, Optional
import os

from note_service.AI.gemini_client import GeminiClient


class AIService:
    """
    Thin wrapper around GeminiClient that centralizes model configuration
    and exposes a couple of convenience helpers.

    Other services (e.g., SummarizeService, future QuizService) should depend
    on this instead of talking to GeminiClient directly.
    """

    def __init__(
        self,
        gemini: Optional[GeminiClient] = None,
        model: Optional[str] = None,
    ) -> None:
        model_name = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.gemini = gemini or GeminiClient(model=model_name)

    def generate_json(
        self,
        prompt: str,
        *,
        schema_hint: Optional[Dict[str, Any]] = None,
        temperature: float = 0.2,
    ) -> Dict[str, Any]:
        """
        Generic JSON generation helper. All structured AI features
        (summaries, quizzes, flashcards, etc.) should call through here.
        """
        return self.gemini.generate_json(
            prompt,
            schema_hint=schema_hint,
            temperature=temperature,
        )

    def generate_text(
        self,
        prompt: str,
        *,
        temperature: float = 0.2,
    ) -> str:
        return self.gemini.generate_text(prompt, temperature=temperature)