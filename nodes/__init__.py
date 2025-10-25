from .input_processing import (
    input_processing_node,
    input_router_node
)

from .processing import (
    process_code_node,
    process_docs_node,
    process_both_node
)

from .research.coordinator import research_coordinator_node
from .research.researcher import research_node

from .drafting import (
    blog_structuring_node,
    section_drafting_node
)

from .introduction import (
    introduction_synthesis_node,
    conditional_research_synthesis_node
)

from .plagiarism import (
    plagiarism_check_node,
    evaluate_plagiarism_node,
    rewrite_section_node
)

from .completion import completion_node