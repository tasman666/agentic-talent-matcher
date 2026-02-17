# Agentic Talent Matcher 🧩

An intelligent recruitment assistant powered by AI agents. It matches candidates with job opportunities by searching internal databases, Ciklum's career portal, and LinkedIn simultaneously.

## Features

- **Multi-Source Search**:
  - **Internal Database**: Semantic search over candidate CVs (PDFs) using Qdrant vector store.
  - **Ciklum Careers**: Real-time integration with Ciklum's job board.
  - **LinkedIn**: Search for external job opportunities and post updates.
- **Smart Matching Agent**:
  - Uses **LangChain** and **LLMs** (Ollama, OpenAI, Gemini) to reason about skills and requirements.
  - Generates comprehensive summaries with direct links to job offers.
  - Auto-evaluates its own performance (Relevance, Clarity, Accuracy) using an LLM-as-a-Judge.
- **Modern UI**:
  - **Streamlit**-based chat interface.
  - Drag-and-drop CV upload.
  - Real-time response evaluation.
- **Extensible Architecture**:
  - Built with **FastAPI** for robust backend services.
  - Container-ready structure.

## Tech Stack

- **Backend**: Python, FastAPI, Pydantic
- **AI/LLM**: LangChain, LangGraph, Ollama (Local LLMs), OpenAI/Anthropic/Google support
- **Vector Database**: Qdrant (Hybrid Search: Dense + Splade Sparse)
- **Frontend**: Streamlit
- **PDF Processing**: PyMuPDF (fitz), SemanticChunker
- **Testing**: End-to-End simulation script

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repo-url>
   cd agentic-talent-matcher
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Convert and configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings (LLM_MODEL_NAME, API keys, etc.)
   ```

## Usage

### 1. Start the Backend API
Run the FastAPI server:
```bash
uvicorn main:app --reload --port 8000
```
API Documentation is available at `http://localhost:8000/docs`.

### 2. Start the Frontend UI
In a separate terminal, run the Streamlit app:
```bash
streamlit run ui.py
```
The UI will open in your browser (usually `http://localhost:8501`).

### 3. Upload CVs
- Use the **Upload CVs** sidebar in the UI to upload PDF resumes.
- Alternatively, generate sample CVs for testing:
  ```bash
  python scripts/generate_samples.py
  ```
  The generated files will be located in the `sample_cvs` directory.

### 4. Ask the Agent
- "Find a Senior Java Developer and matching Ciklum jobs."
- "Find Python jobs on LinkedIn for a junior candidate."
- "Write a LinkedIn post about yourself."

## Configuration (.env)

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_MODEL_NAME` | Model to use (provider:model) | `ollama:llama3.2:latest` |
| `LLM_BASE_URL` | Base URL for local LLMs | `http://localhost:11434` (Ollama) |
| `EVALUATION_LLM_MODEL_NAME` | Model for judging responses | Same as `LLM_MODEL_NAME` |
| `QDRANT_HOST` | Qdrant host (or path for local) | `:memory:` (Local) |
| `LINKEDIN_ACCESS_TOKEN` | Token for posting to LinkedIn | (Optional) |

## Testing

Run the end-to-end simulation script to verify all components (Indexing, Search, Agent, Evaluation):
```bash
python scripts/test_end_to_end.py
```
A comprehensive report will be generated in `test_report.md`.

## License

MIT
