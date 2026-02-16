from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.embeddings import HuggingFaceEmbeddings
import fitz

from app.config import get_settings


class PDFService:
    def __init__(self):
        settings = get_settings()
        # We use a lightweight model for the splitting logic itself
        self.embeddings = HuggingFaceEmbeddings(model_name=settings.chunker_model_name)
        self.splitter = SemanticChunker(
            self.embeddings, 
            breakpoint_threshold_type=settings.chunker_breakpoint_type,
        )

    def extract_and_chunk(self, pdf_bytes: bytes) -> list[str]:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        full_text = " ".join([page.get_text() for page in doc])
        
        # This will now return chunks based on meaning, not character count!
        chunks = self.splitter.split_text(full_text)
        return chunks