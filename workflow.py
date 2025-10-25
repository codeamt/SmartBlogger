from langgraph.graph import StateGraph, END
from state import EnhancedBlogState
from nodes import *

def build_workflow():
    builder = StateGraph(EnhancedBlogState)
    
    # Add all nodes (only existing callables)
    nodes = [
        ("process_inputs", input_processing_node),
        ("route_inputs", input_router_node),
        ("process_code", process_code_node),
        ("process_docs", process_docs_node),
        ("process_both", process_both_node),
        ("research_coordinator", research_coordinator_node),
        ("conduct_research", research_node),
        ("blog_structuring", blog_structuring_node),
        ("conditional_synthesis", conditional_research_synthesis_node),
        ("introduction_synthesis", introduction_synthesis_node),
        ("draft_section", section_drafting_node),
        ("plagiarism_check", plagiarism_check_node),
        ("evaluate_plagiarism", evaluate_plagiarism_node),
        ("rewrite_section", rewrite_section_node),
        ("completion", completion_node),
    ]
    
    for name, node in nodes:
        builder.add_node(name, node)
    
    # Set entry point
    builder.set_entry_point("process_inputs")

    # Deterministic edges where next node is fixed
    builder.add_edge("process_inputs", "route_inputs")
    builder.add_edge("process_code", "research_coordinator")
    builder.add_edge("process_docs", "research_coordinator")
    builder.add_edge("process_both", "research_coordinator")
    builder.add_edge("research_coordinator", "conduct_research")
    builder.add_edge("conduct_research", "blog_structuring")
    builder.add_edge("blog_structuring", "conditional_synthesis")
    builder.add_edge("conditional_synthesis", "introduction_synthesis")
    builder.add_edge("introduction_synthesis", "draft_section")
    builder.add_edge("draft_section", "plagiarism_check")
    builder.add_edge("plagiarism_check", "evaluate_plagiarism")
    builder.add_edge("rewrite_section", "plagiarism_check")
    builder.add_edge("completion", END)

    # Conditional routing based on state.next_action
    builder.add_conditional_edges(
        "route_inputs",
        lambda s: s.next_action,
        {"process_code": "process_code", "process_docs": "process_docs", "process_both": "process_both"}
    )

    builder.add_conditional_edges(
        "evaluate_plagiarism",
        lambda s: s.next_action,
        {"rewrite_section": "rewrite_section", "draft_section": "draft_section", "completion": "completion"}
    )
    
    return builder.compile()
    
# Create the workflow
workflow = build_workflow()