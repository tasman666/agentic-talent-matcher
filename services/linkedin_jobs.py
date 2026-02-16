"""
LinkedIn Jobs Search Service.
Scrapes publicly available LinkedIn job search results.

Note: This uses LinkedIn's public job search pages. For production use,
consider using an official LinkedIn API partnership or a licensed
third-party provider.
"""

import httpx
from typing import Optional
import json
import re


LINKEDIN_JOB_SEARCH_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
LINKEDIN_JOB_URL_TEMPLATE = "https://www.linkedin.com/jobs/view/{job_id}"


def search_linkedin_jobs(
    keywords: str,
    location: Optional[str] = None,
    limit: int = 10,
) -> list[dict]:
    """
    Search for jobs on LinkedIn using public guest API.

    Args:
        keywords: Search keywords (e.g. "Java Developer", "Python Engineer").
        location: Optional location filter (e.g. "Poland", "Remote").
        limit: Maximum number of results to return.

    Returns:
        A list of job dicts with title, company, location, url, posted_date.
    """
    params = {
        "keywords": keywords,
        "start": 0,
        "count": limit,
    }
    if location:
        params["location"] = location

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

    try:
        with httpx.Client(timeout=30.0, follow_redirects=True) as client:
            response = client.get(
                LINKEDIN_JOB_SEARCH_URL,
                params=params,
                headers=headers,
            )
            response.raise_for_status()
            html = response.text
    except httpx.HTTPError as e:
        return [{"error": f"Failed to fetch LinkedIn jobs: {str(e)}"}]

    return _parse_linkedin_jobs_html(html)


def _parse_linkedin_jobs_html(html: str) -> list[dict]:
    """
    Parse job listings from LinkedIn's guest job search HTML response.
    """
    jobs = []

    # LinkedIn guest API returns a list of <li> elements with job cards
    # Each job card is inside a <div class="base-card">
    job_card_pattern = re.compile(
        r'<div[^>]*class="[^"]*base-card[^"]*"[^>]*data-entity-urn="urn:li:jobPosting:(\d+)"[^>]*>',
        re.DOTALL,
    )

    # Split HTML into individual job cards
    cards = job_card_pattern.finditer(html)
    card_positions = []
    for match in cards:
        card_positions.append((match.start(), match.group(1)))

    for i, (start, job_id) in enumerate(card_positions):
        end = card_positions[i + 1][0] if i + 1 < len(card_positions) else len(html)
        card_html = html[start:end]

        title = _extract_text(card_html, r'class="base-search-card__title"[^>]*>([^<]+)')
        company = _extract_text(card_html, r'class="hidden-nested-link"[^>]*>([^<]+)')
        location = _extract_text(card_html, r'class="job-search-card__location"[^>]*>([^<]+)')
        posted_date = _extract_text(card_html, r'<time[^>]*datetime="([^"]*)"')

        jobs.append({
            "title": title,
            "company": company,
            "location": location,
            "posted_date": posted_date,
            "url": LINKEDIN_JOB_URL_TEMPLATE.format(job_id=job_id),
            "id": job_id,
            "source": "LinkedIn",
        })

    return jobs


def _extract_text(html: str, pattern: str) -> str:
    """Extract and clean text matching a regex pattern from HTML."""
    match = re.search(pattern, html, re.DOTALL)
    if match:
        return match.group(1).strip()
    return "N/A"
