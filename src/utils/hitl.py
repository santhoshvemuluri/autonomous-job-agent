from typing import Dict, Any
from src.graph.state import AgentState

def hitl_review(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph node: Pauses execution to allow the developer to review 
    the tailored PDF before handing it off to the Browser agent.
    """
    pdf_path = state.get("pdf_path")
    ats_score = state.get("ats_score", 0.0)
    company = state.get("company_name", "Unknown Company")
    title = state.get("job_title", "Target Role")
    
    print("\n" + "="*60)
    print("🛑 HUMAN-IN-THE-LOOP: PRE-SUBMISSION REVIEW 🛑")
    print(f"🏢 Job: {title} @ {company}")
    print(f"🎯 Final ATS Score: {ats_score}/100")
    print(f"📄 Tailored Resume: {pdf_path}")
    print("="*60)
    
    if not pdf_path:
        print("❌ Error: No PDF was generated. Halting.")
        return {"approved_for_submission": False, "submission_status": "Failed: No PDF"}

    print("Please open the PDF file above to verify the layout and content.")
    
    while True:
        response = input("\nDo you approve this resume for automated submission? (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            print("\n✅ Approved. Booting up browser automation...")
            return {"approved_for_submission": True, "submission_status": "Approved for submission"}
        elif response in ['n', 'no']:
            print("\n❌ Rejected. Halting pipeline for this job.")
            return {"approved_for_submission": False, "submission_status": "Halted by user at HITL review"}
        else:
            print("Invalid input. Please enter 'y' or 'n'.")