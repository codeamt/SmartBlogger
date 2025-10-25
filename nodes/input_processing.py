from state import EnhancedBlogState
from utils.file_processing import extract_text_from_pdf


def input_processing_node(state: EnhancedBlogState) -> EnhancedBlogState:
    """Process all available inputs"""
    processed_docs = []

    # Process uploaded files
    if state.uploaded_files:
        for file_path in state.uploaded_files:
            if file_path.endswith(".pdf"):
                processed_docs.append(extract_text_from_pdf(file_path))
            else:  # Assume text file
                try:
                    with open(file_path, "r") as f:
                        processed_docs.append(f.read())
                except:
                    pass

    return state.update(
        documents=processed_docs,
        next_action="route_inputs"
    )


def input_router_node(state: EnhancedBlogState) -> EnhancedBlogState:
    """Route based on available inputs"""
    has_code = bool(state.source_code)
    has_docs = bool(state.documents)

    if has_code and has_docs:
        return state.update(next_action="process_both")
    elif has_code:
        return state.update(next_action="process_code")
    elif has_docs:
        return state.update(next_action="process_docs")
    else:
        raise ValueError("No valid inputs provided")