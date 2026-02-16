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

class EvaluationDetail(BaseModel):
    score: float
    reasoning: str

class EvaluationResult(BaseModel):
    relevance: EvaluationDetail
    clarity: EvaluationDetail
    accuracy: EvaluationDetail
    overall: float

class EvaluationRequest(BaseModel):
    query: str
    response: str
    context: str = ""

class EvaluationResponse(BaseModel):
    metrics: EvaluationResult
