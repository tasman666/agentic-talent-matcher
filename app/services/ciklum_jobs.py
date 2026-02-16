"""
Ciklum Jobs Search Service.
Queries the Oracle HCM Candidate Experience REST API
used by https://explore-jobs.ciklum.com
"""

import httpx
from typing import Optional


CIKLUM_API_BASE = "https://ialmme.fa.ocs.oraclecloud.com"
CIKLUM_JOBS_ENDPOINT = (
    "/hcmRestApi/resources/latest/recruitingCEJobRequisitions"
)
CIKLUM_SITE_NUMBER = "CX_1001"
CIKLUM_JOB_URL_TEMPLATE = (
    "https://explore-jobs.ciklum.com/en/sites/ciklum-career/job/{job_id}"
)


def search_ciklum_jobs(
    keyword: str,
    limit: int = 10,
    location: Optional[str] = None,
) -> list[dict]:
    """
    Search for open positions on the Ciklum careers site.

    Args:
        keyword: Search term (e.g. "Java", "Python Senior Engineer").
        limit: Maximum number of results to return.
        location: Optional location filter.

    Returns:
        A list of job dicts with title, location, workplace_type, posted_date, url.
    """
    finder_params = (
        f"findReqs;"
        f"siteNumber={CIKLUM_SITE_NUMBER},"
        f"facetsList=LOCATIONS;WORK_LOCATIONS;WORKPLACE_TYPES;TITLES;CATEGORIES;ORGANIZATIONS;POSTING_DATES;FLEX_FIELDS,"
        f"limit={limit},"
        f"keyword={keyword},"
        f"lastSelectedFacet=POSTING_DATES,"
        f"selectedCategoriesFacet=,"
        f"selectedFlexFieldsFacets=,"
        f"selectedLocationsFacet=,"
        f"selectedPostingDatesFacet=,"
        f"selectedOrganizationsFacet=,"
        f"selectedTitlesFacet=,"
        f"selectedWorkLocationsFacet=,"
        f"selectedWorkplaceTypesFacet=,"
        f"sortBy=POSTING_DATES_DESC"
    )

    params = {
        "onlyData": "true",
        "expand": "requisitionList.secondaryLocations,flexFieldsFacet.values",
        "finder": finder_params,
    }

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(
                f"{CIKLUM_API_BASE}{CIKLUM_JOBS_ENDPOINT}",
                params=params,
            )
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPError as e:
        return [{"error": f"Failed to fetch Ciklum jobs: {str(e)}"}]

    items = data.get("items", [])
    if not items:
        return []

    search_result = items[0]
    requisitions = search_result.get("requisitionList", [])
    total = search_result.get("TotalJobsCount", 0)

    jobs = []
    for req in requisitions:
        job = {
            "title": req.get("Title", "N/A"),
            "id": req.get("Id"),
            "location": req.get("PrimaryLocation", "N/A"),
            "country_code": req.get("PrimaryLocationCountry", "N/A"),
            "workplace_type": req.get("WorkplaceType", "N/A"),
            "posted_date": req.get("PostedDate", "N/A"),
            "url": CIKLUM_JOB_URL_TEMPLATE.format(job_id=req.get("Id", "")),
            "source": "Ciklum",
        }
        jobs.append(job)

    return jobs
