# -*- coding: utf-8 -*-
"""
Gemini JSON client used by SummarizeService.

Usage:
    client = GeminiClient()  # GEMINI_API_KEY env must be set
    data = client.generate_json(prompt, schema_hint={...}, temperature=0.2)
"""

import os
import json
import re
from typing import Any, Dict, Optional
import google.generativeai as genai

# --------------------------
# Robust JSON parsing helpers
# --------------------------

def _strip_md_fences(s: str) -> str:
    s = s.strip()
    if s.startswith("```"):
        s = re.sub(r"^```(?:json)?\s*", "", s, flags=re.I)
        s = re.sub(r"\s*```$", "", s)
    return s.strip()

def _extract_json_window(s: str) -> str:
    first = s.find("{")
    last = s.rfind("}")
    if first != -1 and last != -1 and last > first:
        return s[first:last+1]
    return s

def _repair_trailing_commas(s: str) -> str:
    return re.sub(r",\s*([}\]])", r"\1", s)

def _balance_brackets(s: str) -> str:
    opens = s.count("{"); closes = s.count("}")
    if opens > closes:
        s += "}" * (opens - closes)
    opens = s.count("["); closes = s.count("]")
    if opens > closes:
        s += "]" * (opens - closes)
    return s

def _coerce_schema(obj: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(obj, dict):
        obj = {}
    def _listify(x):
        if x is None: return []
        if isinstance(x, list): return [str(v) for v in x]
        return [str(x)]
    return {
        "title": str(obj.get("title") or ""),
        "tldr": str(obj.get("tldr") or obj.get("summary") or ""),
        "key_points": _listify(obj.get("key_points")),
        "action_items": _listify(obj.get("action_items")),
        "questions": _listify(obj.get("questions")),
        "keywords": _listify(obj.get("keywords")),
    }

def _parse_json_best_effort(raw: str) -> Dict[str, Any]:
    """Never raises; always returns a dict with expected keys."""
    if not isinstance(raw, str):
        return _coerce_schema({})
    s = _strip_md_fences(raw)
    s = _extract_json_window(s)
    s = _repair_trailing_commas(s)
    s = _balance_brackets(s)
    try:
        return _coerce_schema(json.loads(s))
    except Exception:
        pass
    # coarse regex fallback
    title = re.search(r'"title"\s*:\s*"([^"]*)"', s)
    tldr = re.search(r'"tldr"\s*:\s*"([^"]*)"', s)
    def grep_list(key):
        m = re.search(rf'"{key}"\s*:\s*$begin:math:display$(.*?)$end:math:display$', s, flags=re.S)
        if not m: return []
        return [t.strip() for t in re.findall(r'"([^"]+)"', m.group(1)) if t.strip()]
    coarse = {
        "title": title.group(1) if title else "",
        "tldr": tldr.group(1) if tldr else "",
        "key_points": grep_list("key_points"),
        "action_items": grep_list("action_items"),
        "questions": grep_list("questions"),
        "keywords": grep_list("keywords"),
    }
    return _coerce_schema(coarse)


# --------------------------
# Gemini client
# --------------------------

DEFAULT_MODEL = "gemini-2.5-flash"

class GeminiClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        system_instruction: Optional[str] = None,
    ):
        """
        Args:
            api_key: uses env GEMINI_API_KEY if None
            model:   Gemini model name
            system_instruction: optional system prompt
        """
        api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set in your environment.")

        genai.configure(api_key=api_key)

        self.model_name = model
        self.system_instruction = system_instruction or (
            "You are a helpful assistant that returns STRICT JSON matching the schema. "
            "Never include markdown fences. Never include commentary outside JSON."
        )
        # Create model instance (cached per client)
        self._model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=self.system_instruction,
            generation_config={"temperature": 0.2},
        )

    # ---- public API ----
    def generate_json(
        self,
        prompt: str,
        schema_hint: Optional[Dict[str, Any]] = None,
        temperature: float = 0.2,
    ) -> Dict[str, Any]:
        """
        Returns a dict with keys: title, tldr, key_points, action_items, questions, keywords.
        Never raises due to JSON formatting; repairs best-effort.
        """
        text = self._call_model(prompt, temperature=temperature)
        return _parse_json_best_effort(text or "")

    # ---- internal ----
    def _call_model(self, prompt: str, temperature: float = 0.2) -> str:
        """
        Calls Gemini and returns raw text. We ask for JSON explicitly via MIME type,
        but still sanitize output in case the model returns stray text.
        """
        try:
            resp = self._model.generate_content(
                [
                    {
                        "role": "user",
                        "parts": [prompt],
                    }
                ],
                generation_config={
                    "temperature": temperature,
                    "response_mime_type": "application/json",
                },
            )
            # google-generativeai returns .text for convenience
            return (resp.text or "").strip()
        except Exception as e:
            # Return empty JSON so upstream can still persist a valid shape
            return "{}"

__all__ = ["GeminiClient"]