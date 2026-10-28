import json
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from src.graph.state import AgentState


# Pydantic schema for structured output to maintain clean state separation
class TailoredResumeOutput(BaseModel):
    extracted_keywords: List[str] = Field(
        description="Key technical skills, libraries, and frameworks extracted from the JD"
    )
    tailored_markdown: str = Field(
        description="The full ATS-compliant resume rendered in pure single-column Markdown"
    )

# Strict System Prompt enforcing Fresher Invariants and ATS Formatting
TAILOR_SYSTEM_PROMPT = """You are an elite technical resume strategist specializing in entry-level (0-1 YOE) Data Analyst, Machine Learning, and AI Engineering roles.

Your task is to tailor a candidate's resume for a specific Job Description (JD) using strictly verified ground truth data from their Master Profile.

========================================
CRITICAL GROUND TRUTH INVARIANTS:
========================================
1. ZERO HALLUCINATION POLICY:
   - You MUST NOT fabricate full-time corporate titles, years of corporate tenure, or employment history.
   - Do NOT invent companies, internships, open-source projects, or credentials not explicitly present in the Master Profile.
   - Do NOT add tools, frameworks, or languages to the resume unless they are explicitly present in the candidate's skills, projects, or experience records.

2. REFRAMING & KEYWORD INTEGRATION:
   - Match the candidate's actual projects, coursework, and internship records directly against the JD keywords.
   - Contextualize existing experience using the technical vocabulary of the target JD.
   - Project bullets must follow the Action-Context-Metric format: [Strong Action Verb] + [Specific Technical Method/Tool] + [Quantifiable Impact].

3. ATS FORMAT & MARKDOWN STRUCTURE:
   - Single-column plain text Markdown ONLY.
   - NO tables, columns, callout boxes, icons, or complex ASCII dividers.
   - Standard uppercase section headings:
     # [CANDIDATE FULL NAME]
     [Email] | [LinkedIn URL] | [GitHub URL] | [Portfolio URL]

     ## PROFESSIONAL SUMMARY
     3-4 lines highlighting core competency, target role, and key tools matching the JD.

     ## TECHNICAL SKILLS
     - Languages: ...
     - Frameworks & Libraries: ...
     - Developer & Cloud Tools: ...
     - Core Competencies: ...

     ## TECHNICAL PROJECTS
     ### [Project Name] | [Key Tech Stack]
     - Bullet 1
     - Bullet 2

     ## EXPERIENCE / INTERNSHIPS
     ### [Role] - [Company/Organization]
     - Bullet 1
     - Bullet 2

     ## EDUCATION
     [Degree], [Institution]

     ## CERTIFICATIONS
     - [Certification Name] - [Issuing Body]
"""

TAILOR_USER_PROMPT = """Review the following inputs and generate the tailored resume:

### Target Job Description:
{job_description}

### Verified Master Candidate Profile:
{master_profile_json}

### Previous Evaluator Feedback (if iterating):
{evaluator_feedback}

### Missing Keywords Identified from Previous Run:
{missing_keywords}

Generate the extracted keywords and the complete ATS-compliant Markdown resume. Ensure every project and bullet remains strictly true to the profile.
"""

def get_tailor_chain():
    """Initializes the Groq chain with structured output."""
    llm = ChatGroq(
        # Use your custom available 120B model
        model="openai/gpt-oss-120b", 
        temperature=0.1,
        max_tokens=3000,
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", TAILOR_SYSTEM_PROMPT),
        ("human", TAILOR_USER_PROMPT),
    ])
    
    return prompt | llm.with_structured_output(TailoredResumeOutput)

def tailor_resume(state: AgentState) -> Dict[str, Any]:
    """LangGraph node execution function for resume tailoring."""
    chain = get_tailor_chain()
    
    # Serialize master profile ground truth
    master_profile_json = json.dumps(state.get("master_profile", {}), indent=2)
    
    # Prepare previous feedback if this is an iterative refinement run
    feedback = state.get("evaluator_feedback", "Initial generation - no prior feedback.")
    missing_kw = ", ".join(state.get("missing_keywords", [])) or "None identified."
    
    inputs = {
        "job_description": state.get("job_description", ""),
        "master_profile_json": master_profile_json,
        "evaluator_feedback": feedback,
        "missing_keywords": missing_kw,
    }
    
    result: TailoredResumeOutput = chain.invoke(inputs)
    current_iteration = state.get("iteration_count", 0)
    
    return {
        "tailored_resume_markdown": result.tailored_markdown,
        "extracted_keywords": result.extracted_keywords,
        "iteration_count": current_iteration + 1,
    }