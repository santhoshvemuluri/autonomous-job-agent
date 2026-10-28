import os
import asyncio
from browser_use import Agent
from langchain_google_genai import ChatGoogleGenerativeAI

async def execute_browser_task(task_prompt: str) -> str:
    """Asynchronously runs the browser-use Agent."""
    
    # Use native Google GenAI
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.0
    )
    
    # FIX: Dynamically inject the provider attribute that browser-use expects!
    llm.provider = "google"
    
    agent = Agent(
        task=task_prompt,
        llm=llm,
        use_vision=True
    )
    
    result = await agent.run()
    return str(result)

def apply_job(state: dict) -> dict:
    """LangGraph node function that triggers the browser application."""
    pdf_path = state.get("pdf_path", "")
    job_description = state.get("job_description", "")
    
    task_prompt = (
        f"Find the job application page for this role based on this description: {job_description}. "
        f"Navigate through the form, fill in standard entry-level developer details, "
        f"and upload the resume located precisely at this file path: {os.path.abspath(pdf_path)}. "
        f"Submit the application."
    )
    
    print("\n🚀 [Browser Applier] Initializing automated application process...")
    
    try:
        result = asyncio.run(execute_browser_task(task_prompt))
        return {"application_status": "Success", "browser_logs": result}
    except Exception as e:
        print(f"\n❌ [Browser Applier] Failed during execution: {e}")
        return {"application_status": f"Failed: {str(e)}"}