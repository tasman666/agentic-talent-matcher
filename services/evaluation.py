"""
Evaluation Service.
Measures agent effectiveness using LLM-as-a-Judge approach.
Scores:
- **Relevance**: Does the response directly address the user's query?
- **Clarity**: Is the response concise, well-structured, and easy to understand?
- **Accuracy**: Does the response align with the retrieved context (if provided)?
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from config import get_settings
from services.llm_factory import create_llm
from schemas import EvaluationResult, EvaluationDetail


EVALUATION_PROMPT = """\
You are an expert evaluator for a talent matching AI agent.
Your task is to evaluate the quality of the AI's response based on the
user's query and the context provided.

Evaluate the response on the following criteria (1-5 scale):

1. **Relevance**: Does the response directly address the user's query?
   - 5: Perfectly relevant, addresses all parts of the query.
   - 1: Completely irrelevant.

2. **Clarity**: Is the response concise, well-structured, and easy to understand?
   - 5: Crystal clear, excellent structure.
   - 1: Confusing, verbose, or poorly formatted.

3. **Accuracy**: create score based on how well the response leverages the provided context
   (candidate profiles, job listings). Does it hallucinate or miss key details?
   - 5: Highly accurate, fully supported by context.
   - 1: Major inaccuracies or hallucinations.

**Input:**
- Query: {query}
- Response: {response}
- Context (Retrieved Data): {context}

**Output Format:**
Return a JSON object with the following structure:
{{
    "relevance": {{"score": <int>, "reasoning": "<string>"}},
    "clarity": {{"score": <int>, "reasoning": "<string>"}},
    "accuracy": {{"score": <int>, "reasoning": "<string>"}}
}}
"""


async def evaluate_agent_response(
    query: str,
    response: str,
    context: str = "No explicit context provided.",
) -> EvaluationResult:
    """
    Evaluates the agent's response using an LLM judge.
    Returns the schema-defined EvaluationResult.
    """
    settings = get_settings()

    # Use a capable model for evaluation (default to configured LLM)
    llm = create_llm(
        model_name=settings.llm_model_name,
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        temperature=0.0,
    )

    prompt = ChatPromptTemplate.from_template(EVALUATION_PROMPT)
    chain = prompt | llm | JsonOutputParser()

    try:
        result = await chain.ainvoke({
            "query": query,
            "response": response,
            "context": context,
        })

        # Calculate overall average
        relevance_score = result.get("relevance", {}).get("score", 0)
        clarity_score = result.get("clarity", {}).get("score", 0)
        accuracy_score = result.get("accuracy", {}).get("score", 0)

        scores = [relevance_score, clarity_score, accuracy_score]
        overall = sum(scores) / len(scores) if scores else 0.0

        return EvaluationResult(
            relevance=EvaluationDetail(**result["relevance"]),
            clarity=EvaluationDetail(**result["clarity"]),
            accuracy=EvaluationDetail(**result["accuracy"]),
            overall=round(overall, 2),
        )

    except Exception as e:
        # Fallback if evaluation fails
        error_detail = EvaluationDetail(score=0, reasoning=f"Evaluation failed: {str(e)}")
        return EvaluationResult(
            relevance=error_detail,
            clarity=error_detail,
            accuracy=error_detail,
            overall=0.0,
        )
