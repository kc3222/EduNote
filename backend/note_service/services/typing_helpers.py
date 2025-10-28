from typing import Dict, List, TypedDict

class SummaryDict(TypedDict):
    title: str
    tldr: str
    key_points: List[str]
    action_items: List[str]
    questions: List[str]
    keywords: List[str]