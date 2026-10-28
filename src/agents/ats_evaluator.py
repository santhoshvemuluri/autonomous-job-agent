import json
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from src.graph.state import AgentState

# Pydantic v2 schema for deterministic, structured ATS scoring
class ATSEvaluationOutput(BaseModel):
    hard_skill_score: float = Field(
        ge=0, le=50,
        description="Score from 0 to 50 based on presence of mandatory JD tools, libraries, and frameworks."
    )
    context_alignment_score: float = Field(
        ge=0, le=30,
        description="Score from 0 to 30 evaluating whether candidate projects reflect the target problems in the JD."
    )
    formatting_score: float = Field(
        ge=0, le=20,
        description="Score from 0 to 20 evaluating ATS plain-text parsing compatibility (standard headers, single column, clean bullets)."
    )
    total_score: float = Field(
        ge=0, le=100,
        description="Sum of hard_skill_score, context_alignment_score, and formatting_score."
    )
    extracted_jd_skills: List[str] = Field(
        description="All hard technical skills and tools extracted from the Job Description."
    )
    missing_critical_keywords: List[str] = Field(
        description="Mandatory skills or tools found in the JD that are completely missing from the candidate's resume draft."
    )
    refinement_instructions: str = Field(
        description="Specific, actionable guidance for the Tailor Agent to improve the resume without fabricating experience."
    )

ATS_EVALUATOR_SYSTEM_PROMPT = """You are an algorithmic Applicant Tracking System (ATS) evaluator and hiring committee auditor.
Your job is to rigorously evaluate a tailored resume against a target Job Description (JD).

Scoring Rubric (Strictly Max 100 Points Total):
1. Hard Skill Overlap (0 - 50 Points):
   - Measure the exact keyword match ratio for mandatory languages, libraries, platforms, and databases in the JD.
   - 45-50: >=90% of essential technical skills matched.
   - 35-44: 75-89% matched.
   - 20-34: 50-74% matched.
   - <20: <50% matched.

2. Contextual & Project Alignment (0 - 30 Points):
   - Assess whether project bullets solve domain-relevant problems reflecting the JD.
   - Check if metrics, action verbs, and technical applications (e.g., ETL, model evaluation, visualization) are clearly demonstrated.

3. ATS Formatting & Parsing Compatibility (0 - 20 Points):
   - Award full 20 points if: Strict single-column layout, standard uppercase headers (SUMMARY, TECHNICAL SKILLS, PROJECTS, EXPERIENCE, EDUCATION, CERTIFICATIONS), standard bullet characters, no Markdown tables or multi-column grids.
   - Deduct points for unsupported characters, non-standard headers, or nested formatting.

CRITICAL INSTRUCTIONS FOR REFINEMENT FEEDBACK:
- If total_score < 90, write concise, actionable refinement instructions.
- Do NOT advise inventing corporate jobs or skills absent from the ground truth profile.
- Explicitly list missing critical keywords so the Tailor Agent can highlight them where legitimate synonyms or existing projects exist.
"""

ATS_EVALUATOR_USER_PROMPT = """Evaluate this tailored resume draft against the target Job Description:

### Target Job Description:
{job_description}

### Tailored Resume Draft (Markdown):
{tailored_resume_markdown}

Perform independent step-by-step scoring according to the rubric and return the structured evaluation.
"""

def get_evaluator_chain():
    """Builds the evaluation chain using Groq with structured output."""
    llm = ChatGroq(
        # Use your custom available 120B model
        model="openai/gpt-oss-120b",
        temperature=0.0, 
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", ATS_EVALUATOR_SYSTEM_PROMPT),
        ("human", ATS_EVALUATOR_USER_PROMPT),
    ])
    
    return prompt | llm.with_structured_output(ATSEvaluationOutput)

def evaluate_ats(state: AgentState) -> Dict[str, Any]:
    """LangGraph node that computes the ATS score and prepares feedback for refinement."""
    chain = get_evaluator_chain()
    
    jd = state.get("job_description", "")
    resume_md = state.get("tailored_resume_markdown", "")
    current_iteration = state.get("iteration_count", 1)
    
    # Run evaluation
    result: ATSEvaluationOutput = chain.invoke({
        "job_description": jd,
        "tailored_resume_markdown": resume_md
    })
    
    # Compute verified total score
    calculated_total = round(
        result.hard_skill_score + result.context_alignment_score + result.formatting_score, 
        2
    )
    final_score = min(calculated_total, 100.0)
    
    print(f"\n--- [ATS Evaluation Iteration #{current_iteration}] ---")
    print(f"Hard Skills: {result.hard_skill_score}/50")
    print(f"Context Alignment: {result.context_alignment_score}/30")
    print(f"Formatting: {result.formatting_score}/20")
    print(f"Total ATS Score: {final_score}/100")
    if result.missing_critical_keywords:
        print(f"Missing Keywords: {', '.join(result.missing_critical_keywords)}")
    print(f"---------------------------------------------------\n")

    return {
        "ats_score": final_score,
        "missing_keywords": result.missing_critical_keywords,
        "evaluator_feedback": result.refinement_instructions,
    }