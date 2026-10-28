import re
from typing import Dict, Any
from src.graph.state import AgentState

# Compile regex patterns for efficiency
# Drop patterns: Matches mid/senior level indicators and strict YOE requirements
BLACKLIST_REGEX = re.compile(
    r"(?i)\b(2\+?\s*years?|3\+?\s*years?|4\+?\s*years?|5\+?\s*years?|senior|lead|principal|staff|manager|director|vp|head)\b"
)

# Accept patterns: Matches strict entry-level and fresher indicators
WHITELIST_REGEX = re.compile(
    r"(?i)\b(0-1\s*years?|entry[\s-]?level|fresher|graduate|junior|intern|0\s*years?)\b"
)

def filter_fresher(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph entry node: evaluates if a job meets the 0-1 YOE fresher invariant.
    Uses regex to enforce deterministic inclusion/exclusion before invoking the LLMs.
    """
    title = state.get("job_title", "")
    jd = state.get("job_description", "")
    
    # Combine title and JD for holistic scanning
    full_text = f"{title}\n{jd}"
    
    print(f"\n--- [Scout Filter Node] ---")
    print(f"Evaluating: {title} at {state.get('company_name', 'Unknown')}")

    # 1. Immediate rejection if blacklist terms are found (Overrides whitelist)
    blacklist_match = BLACKLIST_REGEX.search(full_text)
    if blacklist_match:
        print(f"❌ REJECTED: Found senior/experienced keyword: '{blacklist_match.group(0).strip()}'")
        return {"is_fresher_eligible": False}

    # 2. Strong acceptance if explicit whitelist terms are found
    whitelist_match = WHITELIST_REGEX.search(full_text)
    if whitelist_match:
        print(f"✅ ACCEPTED: Found explicit fresher keyword: '{whitelist_match.group(0).strip()}'")
        return {"is_fresher_eligible": True}

    # 3. Implicit acceptance (Lack of strict corporate tenure prerequisites)
    # If the JD doesn't explicitly mention "3+ years" or "Senior", pass it to the ATS Evaluator to decide contextually.
    print("⚠️ ACCEPTED (Implicit): No senior keywords found. Assuming eligible.")
    return {"is_fresher_eligible": True}

# ---------------------------------------------------------
# Helper function to mock scraped jobs for local testing
# ---------------------------------------------------------
def get_mock_job() -> dict:
    """Simulates a scraped job from Wellfound or YC Work at a Startup."""
    return {
        "job_id": "job_10293",
        "job_title": "Junior Data Analyst",
        "company_name": "TechFlow Analytics",
        "job_url": "https://example.com/apply/10293",
        "job_description": (
            "We are looking for a Junior Data Analyst to join our team. "
            "You should be familiar with Python, Pandas, and SQL for data extraction and cleaning. "
            "Experience with BI tools like Tableau is a plus. "
            "0-1 years of experience required. Must be comfortable building ETL pipelines."
        )
    }