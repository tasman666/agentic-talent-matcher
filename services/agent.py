"""
Talent Matching Agent.
Uses LangChain to orchestrate candidate search and job matching
across multiple sources: local CV database, Ciklum careers, and LinkedIn.
Supports OpenAI, Google Gemini, and Anthropic Claude via LLM_MODEL_NAME config.
"""

import json
import httpx
from typing import Optional

from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent

from config import get_settings
from services.llm_factory import create_llm
from services.ciklum_jobs import search_ciklum_jobs
from services.linkedin_jobs import search_linkedin_jobs


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@tool
def search_candidates(query: str, limit: int = 5) -> str:
    """
    Search the internal CV database for candidates matching the query.
    Use this to find candidates whose resumes match specific skills,
    technologies, or job descriptions.

    Args:
        query: Natural-language search query (e.g. "Senior Java developer with Spring Boot experience").
        limit: Maximum number of candidate results to return (default 5).
    """
    settings = get_settings()
    base_url = f"http://localhost:{settings.app_port}"
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(
                f"{base_url}/search/",
                params={"query": query, "limit": limit},
            )
            response.raise_for_status()
            return json.dumps(response.json(), indent=2)
    except httpx.HTTPError as e:
        return json.dumps({"error": f"Candidate search failed: {str(e)}"})


@tool
def find_ciklum_jobs(keyword: str, limit: int = 10) -> str:
    """
    Search for open job positions on the Ciklum careers page.
    Use this to find jobs at Ciklum that match candidate skills.

    Args:
        keyword: Search keyword (e.g. "Java", "Python", "QA Engineer").
        limit: Maximum number of job results to return (default 10).
    """
    jobs = search_ciklum_jobs(keyword=keyword, limit=limit)
    return json.dumps(jobs, indent=2)


@tool
def find_linkedin_jobs(
    keywords: str,
    location: Optional[str] = None,
    limit: int = 10,
) -> str:
    """
    Search for open job positions on LinkedIn.
    Use this to find jobs on the broader market that match candidate skills.

    Args:
        keywords: Search keywords (e.g. "Senior Java Developer").
        location: Optional location filter (e.g. "Poland", "Remote", "Germany").
        limit: Maximum number of job results to return (default 10).
    """
    jobs = search_linkedin_jobs(keywords=keywords, location=location, limit=limit)
    return json.dumps(jobs, indent=2)


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
You are a Talent Matching Agent for a recruitment company. Your goal is to
help recruiters find the best job opportunities for their candidates.

Given information about a candidate (skills, experience, preferences), you should:

1. **Search the internal CV database** to find matching candidate profiles
   using the search_candidates tool.
2. **Search Ciklum's job board** for relevant open positions using
   the find_ciklum_jobs tool.
3. **Search LinkedIn** for additional job opportunities using the
   find_linkedin_jobs tool.

After gathering results from all sources, provide a comprehensive summary:
- List the most relevant candidates found in the database
- List the best matching Ciklum jobs with links
- List the best matching LinkedIn jobs with links
- Provide a brief recommendation on the best matches

Be concise but thorough. Always search ALL three sources before providing
your final answer (unless query specify only one specificsource). Use multiple search queries if the initial results
aren't specific enough.
"""

TOOLS = [search_candidates, find_ciklum_jobs, find_linkedin_jobs]


def create_talent_agent():
    """Create and return the talent matching agent."""
    settings = get_settings()

    llm = create_llm(
        model_name=settings.llm_model_name,
        api_key=settings.llm_api_key,
        temperature=settings.llm_temperature,
    )

    agent = create_react_agent(
        model=llm,
        tools=TOOLS,
        prompt=SYSTEM_PROMPT,
    )

    return agent


def _extract_text_content(content) -> str:
    """
    Normalize message content to a plain string.
    OpenAI returns a str, but Gemini/Anthropic may return a list of
    content blocks like [{'type': 'text', 'text': '...'}].
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block["text"])
            elif isinstance(block, str):
                parts.append(block)
        return "\n".join(parts)
    return str(content)


async def run_talent_agent(query: str) -> str:
    """
    Run the talent matching agent with the given query.

    Args:
        query: Description of what kind of talent/jobs to find
               (e.g. "Find jobs for a Senior Java developer with 5 years
               experience in Spring Boot, preferably remote in Poland").

    Returns:
        The agent's final response as a string.
    """
    agent = create_talent_agent()

    result = await agent.ainvoke(
        {"messages": [HumanMessage(content=query)]},
    )

    # Extract the final AI message
    messages = result.get("messages", [])
    for msg in reversed(messages):
        if msg.type == "ai" and msg.content:
            return _extract_text_content(msg.content)

    return "Agent did not produce a response."
