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

class AgentRequest(BaseModel):
    query: str

class AgentResponse(BaseModel):
    query: str
    response: str
