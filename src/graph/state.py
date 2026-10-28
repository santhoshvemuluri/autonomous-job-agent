from typing import TypedDict, List, Optional, Dict, Any

class AgentState(TypedDict):
    # Job Metadata
    job_id: str
    job_title: str
    company_name: str
    job_url: str
    job_description: str
    is_fresher_eligible: bool
    
    # Ground Truth
    master_profile: Dict[str, Any]
    
    # Tailoring & Iteration State
    tailored_resume_markdown: str
    extracted_keywords: List[str]
    missing_keywords: List[str]
    ats_score: float
    iteration_count: int
    evaluator_feedback: str
    
    # Artifacts & Execution
    pdf_path: Optional[str]
    approved_for_submission: bool
    submission_status: str