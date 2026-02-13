from fastapi import APIRouter, UploadFile, File, Depends
from app.services.pdf_service import PDFService
from app.services.vector_store import VectorStoreService
from app.schemas import SearchResponse, SearchResult

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