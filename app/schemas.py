from pydantic import BaseModel
from typing import List, Dict, Any

class SearchResult(BaseModel):
    id: str
    score: float
    filename: str
    text_preview: str
    metadata: Dict[str, Any]

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]