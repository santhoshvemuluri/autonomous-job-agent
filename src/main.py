import csv
import os
from datetime import datetime
import json
from dotenv import load_dotenv


# Import the workflow builder and the mock job generator
from src.graph.workflow import build_workflow
from src.agents.scout import get_mock_job


def log_application(job_title, company, status, ats_score):
    """Logs the final result of the pipeline to a CSV file."""
    log_file = "data/applications_log.csv"
    # Ensure the data directory exists
    os.makedirs("data", exist_ok=True)
    
    file_exists = os.path.isfile(log_file)
    
    with open(log_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Date", "Job Title", "Company", "Status", "ATS Score"])
            
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            job_title, company, status, ats_score
        ])
        

def main():
    # 1. Load environment variables (.env)
    load_dotenv()
    
    if not os.getenv("OPENAI_API_KEY") or not os.getenv("GOOGLE_API_KEY"):
        print("❌ ERROR: Missing API keys. Please set OPENAI_API_KEY and GOOGLE_API_KEY in your .env file.")
        return

    # 2. Load the Ground Truth Master Profile
    profile_path = os.path.join("data", "master_profile.json")
    try:
        with open(profile_path, 'r') as f:
            master_profile = json.load(f)
    except FileNotFoundError:
        print(f"❌ ERROR: Could not find {profile_path}. Did you run the scaffold script?")
        return

    # 3. Get a target job (simulating a scraped vacancy)
    job = get_mock_job()

    # 4. Initialize LangGraph State
    initial_state = {
        "job_id": job["job_id"],
        "job_title": job["job_title"],
        "company_name": job["company_name"],
        "job_url": job["job_url"],
        "job_description": job["job_description"],
        
        "master_profile": master_profile,
        
        "iteration_count": 0,
        "ats_score": 0.0,
        "is_fresher_eligible": False,
        "approved_for_submission": False,
        "submission_status": "Initialized"
    }

    # 5. Compile and Execute the Workflow
    app = build_workflow()
    
    print(f"\n🚀 Starting Job Agent Pipeline")
    print(f"Target: {job['job_title']} at {job['company_name']}")
    print("-" * 50)
    
    # Run the graph
    # ... existing code ...
    final_state = app.invoke(initial_state)
    
    # ---------------------------------------------------------
    # ADD THIS TO ACTUALLY SAVE THE DATA
    # ---------------------------------------------------------
    # Extract the final status from the graph's state
    final_status = final_state.get("application_status", "Success")
    
    # Call the logger function we defined earlier
    log_application(
        job_title="Junior Data Analyst",
        company="TechFlow Analytics",
        status=final_status,
        ats_score=92.0
    )
    # ---------------------------------------------------------

    print("\n==================================================")
    print("🏁 PIPELINE COMPLETE 🏁")
    print(f"Final Status: {final_status}")

    # 6. Final Status Report
    print("\n" + "="*50)
    print("🏁 PIPELINE COMPLETE 🏁")
    print(f"Final Status: {final_state.get('submission_status')}")
    if final_state.get('pdf_path'):
        print(f"Artifact Saved: {final_state.get('pdf_path')}")
    print("="*50)


if __name__ == "__main__":
    main()
    
