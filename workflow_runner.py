import streamlit as st
from workflow import build_workflow
from state_management import get_initial_state


@st.cache_resource
def get_cached_workflow():
    """Get cached workflow instance"""
    return build_workflow()


def execute_workflow_with_status(user_inputs: dict):
    """Execute workflow with progress status"""
    with st.status("🔄 Generating content...", expanded=True) as status:
        try:
            st.write("Initializing workflow...")
            workflow = get_cached_workflow()

            st.write("Setting up initial state...")
            initial_state = get_initial_state(user_inputs)

            st.write("Executing workflow...")
            result = workflow.invoke(initial_state)

            st.session_state.result = result
            status.update(label="✅ Generation complete!", state="complete")
            st.success("Blog post generated successfully!")

        except Exception as e:
            status.update(label="❌ Generation failed", state="error")
            st.error(f"Error during generation: {str(e)}")
            st.code(str(e))