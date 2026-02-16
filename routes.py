from fastapi import APIRouter, UploadFile, File, Depends
from services.pdf_service import PDFService
from services.vector_store import VectorStoreService
from services.agent import run_talent_agent
from services.evaluation import evaluate_agent_response
from schemas import (
    SearchResponse, SearchResult, AgentRequest, AgentResponse,
    EvaluationRequest, EvaluationResponse, EvaluationResult
)

router = APIRouter()

_vector_store = VectorStoreService()

def get_vector_store():
    return _vector_store

def get_pdf_service():
    return PDFService()

@router.post("/upload-cv/")
async def upload_cv(
    file: UploadFile = File(...),
    vector_store: VectorStoreService = Depends(get_vector_store),
    pdf_service: PDFService = Depends(get_pdf_service)
):
    content = await file.read()
    chunks = pdf_service.extract_and_chunk(content)
    ids = vector_store.upsert_chunks(chunks, file.filename)
    
    return {"filename": file.filename, "chunks_processed": len(ids)}

@router.get("/search/", response_model=SearchResponse)
async def search_cvs(
    query: str, 
    limit: int = 5,
    vector_store: VectorStoreService = Depends(get_vector_store)
):
    points = vector_store.search_hybrid(query, limit)
    
    # Format the points into our nice JSON structure
    formatted_results = [
        SearchResult(
            id=str(p.id),
            score=p.score,
            filename=p.metadata.get("filename", "unknown"),
            text_preview=p.document[:200] + "..." if len(p.document) > 200 else p.document,
            metadata=p.metadata
        )
        for p in points
    ]
    
    return SearchResponse(query=query, results=formatted_results)


@router.post("/agent/match", response_model=AgentResponse)
async def agent_match(request: AgentRequest):
    """
    Use the AI agent to find the best job matches for a candidate.
    The agent searches the internal CV database, Ciklum careers,
    and LinkedIn to provide a comprehensive recommendation.
    """
    result = await run_talent_agent(request.query)
    return AgentResponse(query=request.query, response=result)


@router.post("/agent/evaluate", response_model=EvaluationResponse)
async def evaluate_match(
    request: EvaluationRequest,
    vector_store: VectorStoreService = Depends(get_vector_store)
):
    """
    Evaluate an agent's response for Relevance, Clarity, and Accuracy.
    Uses an LLM-as-a-Judge approach.
    """
    result = await evaluate_agent_response(
        query=request.query,
        response=request.response,
        context=request.context,
        vector_store_service=vector_store
    )
    
    # Map the service result (EvaluationResult from service) to 
    # the schema (EvaluationResult from schemas) if they differ,
    # or just return it directly if fields align.
    # Our schema structure matches the service output structure.
    
    return EvaluationResponse(
        metrics=EvaluationResult(
            relevance=result.relevance,
            clarity=result.clarity,
            accuracy=result.accuracy,
            overall=result.overall_score
        )
    )
