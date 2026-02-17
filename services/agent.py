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


@tool
def publish_linkedin_post(topic: str = "Self-introduction") -> str:
    """
    Generate and PUBLISH a professional LinkedIn post about this AI Agent.
    
    The post content is pre-approved: explains the agent's purpose,
    how it was built (LangChain/FastAPI/Qdrant), mentions 'Ciklum AI Academy',
    and tags @Ciklum.
    
    If 'LINKEDIN_ACCESS_TOKEN' is configured, this tool will actually POST
    to the user's LinkedIn profile. Otherwise, it returns the draft text.
    """
    # 1. Draft the compliant content
    post_content = (
        "Here is a draft for a LinkedIn post:\n\n"
        "🚀 **Excited to introduce myself!**\n\n"
        "I am an intelligent Talent Matching Agent designed to revolutionize recruitment. "
        "Built using **LangChain** and **FastAPI**, I orchestrate complex searches across internal databases, "
        "Ciklum's career portal, and LinkedIn to find the perfect candidate-job fit.\n\n"
        "My creation was driven by the innovative spirit of the **Ciklum AI Academy**, where advanced "
        "agentic workflows come to life. I leverage hybrid vector search (Qdrant) and LLM reasoning "
        "to deliver precise, context-aware recommendations faster than ever.\n\n"
        "Proud to be a part of this journey with @Ciklum!\n\n"
        "#AI #Recruitment #LangChain #CiklumAIAcademy #Innovation"
    )

    # 2. Check for credentials to publish
    settings = get_settings()
    if not settings.linkedin_access_token or not settings.linkedin_user_urn:
        return (
            f"{post_content}\n\n"
            "*(Note: Real posting skipped. Set LINKEDIN_ACCESS_TOKEN and "
            "LINKEDIN_USER_URN in .env to enable auto-posting using the API)*"
        )

    # 3. Publish to LinkedIn API
    api_url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {settings.linkedin_access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }
    
    # LinkedIn UGC Post Payload
    payload = {
        "author": f"urn:li:person:{settings.linkedin_user_urn}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": post_content.replace("**", "") # Remove markdown bold for plain text API
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    try:
        import httpx
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(api_url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            post_id = data.get("id", "Unknown ID")
            return f"✅ **Successfully published to LinkedIn!**\nPost ID: {post_id}\n\nContent:\n{post_content}"
            
    except Exception as e:
        return f"❌ Failed to publish to LinkedIn: {str(e)}\n\nDraft content was:\n{post_content}"


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
You are a Talent Matching Agent for a recruitment company. Your goal is to
help recruiters find the best job opportunities for their candidates.

You have access to the following tools:
1. `search_candidates`: Search internal CV database.
2. `find_ciklum_jobs`: Search Ciklum jobs.
3. `find_linkedin_jobs`: Search LinkedIn jobs.
4. `publish_linkedin_post`: Publish (or draft) a LinkedIn post about yourself.

**CORE WORKFLOW (Talent Matching):**
1. **Understand Constraints**: First, identify if the user specified a particular source (e.g., "only Ciklum jobs", "just internal candidates").
2. **Execute Searches**:
   - If **NO source specified**: Search ALL three: Internal DB (`search_candidates`), Ciklum (`find_ciklum_jobs`), and LinkedIn (`find_linkedin_jobs`).
   - If **Specific Source(s)**: Search ONLY the requested source(s).
3. **Synthesize Results**: Provide a comprehensive summary of findings from the searched sources.
   - **CRITICAL**: For every job offer found (Ciklum or LinkedIn), you MUST include the direct **URL/Link**.
   - Format: `[Job Title](URL) - Location - brief details` or similar.
   - If a URL is missing in the source data, explicitly state "No URL available".

**SECONDARY WORKFLOW (Self-Promotion):**
If the user asks you to write a LinkedIn post about yourself, the project, or your capabilities:
- Use the `publish_linkedin_post` tool to generate and publish the content.

**Guidelines:**
- be concise but thorough.
- default to searching ALL sources unless explicitly restricted.
- Use multiple search queries if initial results are sparse.
"""

TOOLS = [search_candidates, find_ciklum_jobs, find_linkedin_jobs, publish_linkedin_post]


def create_talent_agent():
    """Create and return the talent matching agent."""
    settings = get_settings()

    llm = create_llm(
        model_name=settings.llm_model_name,
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
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
