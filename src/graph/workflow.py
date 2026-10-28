from langgraph.graph import StateGraph, END
from src.graph.state import AgentState

# Import node functions (stubs for actual agent logic)
from src.agents.scout import filter_fresher
from src.agents.tailor import tailor_resume
from src.agents.ats_evaluator import evaluate_ats
from src.utils.pdf_builder import compile_pdf
from src.utils.hitl import hitl_review
from src.agents.applier import apply_job

def route_fresher_check(state: AgentState):
    if state.get("is_fresher_eligible"):
        return "tailor_resume"
    return END

def route_ats_evaluation(state: AgentState):
    score = state.get("ats_score", 0.0)
    iterations = state.get("iteration_count", 0)
    
    if score >= 90.0 or iterations >= 3:
        return "compile_pdf"
    return "tailor_resume"

def route_hitl_approval(state: AgentState):
    if state.get("approved_for_submission"):
        return "apply_job"
    return END

def build_workflow():
    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("filter_fresher", filter_fresher)
    workflow.add_node("tailor_resume", tailor_resume)
    workflow.add_node("evaluate_ats", evaluate_ats)
    workflow.add_node("compile_pdf", compile_pdf)
    workflow.add_node("hitl_review", hitl_review)
    workflow.add_node("apply_job", apply_job)

    # Set Entry Point
    workflow.set_entry_point("filter_fresher")

    # Add Edges & Conditional Routing
    workflow.add_conditional_edges("filter_fresher", route_fresher_check)
    workflow.add_edge("tailor_resume", "evaluate_ats")
    workflow.add_conditional_edges("evaluate_ats", route_ats_evaluation)
    workflow.add_edge("compile_pdf", "hitl_review")
    workflow.add_conditional_edges("hitl_review", route_hitl_approval)
    workflow.add_edge("apply_job", END)

    return workflow.compile()