from state import EnhancedBlogState
from utils.file_processing import extract_text_from_pdf
from models.llm_manager import local_llm_manager
from models.summarizer import summarizer
from typing import Dict, Any
import json
import re


def input_processing_node(state: EnhancedBlogState) -> EnhancedBlogState:
    """Process all available inputs with enhanced summarization and parameter extraction"""
    processed_docs = []
    enriched_summaries = []
    
    # Process uploaded files with enhanced summarization
    if state.uploaded_files:
        for file_path in state.uploaded_files:
            if file_path.endswith(".pdf"):
                content = extract_text_from_pdf(file_path)
                processed_docs.append(content)
                # Generate structured summary
                summary = generate_structured_summary(content, file_path)
                enriched_summaries.append(summary)
            else:  # Assume text file
                try:
                    with open(file_path, "r") as f:
                        content = f.read()
                        processed_docs.append(content)
                        # Generate structured summary
                        summary = generate_structured_summary(content, file_path)
                        enriched_summaries.append(summary)
                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")
                    pass
    
    # Extract comprehensive content intent and constraints from the initial prompt
    intent_data = extract_content_intent_and_constraints(state.source_code or "", state.research_focus or "")
    
    return state.update(
        documents=processed_docs,
        document_summaries=enriched_summaries,
        target_audience=intent_data.get('audience', 'Developers'),
        tone=intent_data.get('tone', 'Professional'),
        post_type=intent_data.get('post_type'),
        content_constraints=intent_data.get('content_constraints'),
        style_preferences=intent_data.get('style_preferences'),
        success_criteria=intent_data.get('success_criteria'),
        next_action="route_inputs"
    )


def input_router_node(state: EnhancedBlogState) -> EnhancedBlogState:
    """Route based on available inputs and request nature"""
    has_code = bool(state.source_code)
    has_docs = bool(state.documents)
    
    # Check for special routing requests (e.g., outline-only)
    route_action = determine_routing_action(state.source_code or "", state.research_focus or "")
    if route_action:
        return state.update(next_action=route_action)

    if has_code and has_docs:
        return state.update(next_action="process_both")
    elif has_code:
        return state.update(next_action="process_code")
    elif has_docs:
        return state.update(next_action="process_docs")
    else:
        raise ValueError("No valid inputs provided")


def generate_structured_summary(content: str, file_path: str) -> str:
    """Generate a structured summary of document content"""
    if not content:
        return "Empty document"
    
    # Determine file type
    file_extension = file_path.split('.')[-1].lower() if '.' in file_path else "txt"
    
    if file_extension in ["py", "js", "java", "cpp", "cs", "go", "rust"]:
        # Code file summarization
        return summarize_code_file(content, file_extension)
    else:
        # General document summarization
        return summarize_general_document(content)


def summarize_code_file(content: str, language: str) -> str:
    """Generate structured summary for code files"""
    try:
        researcher_llm = local_llm_manager.get_researcher()
        prompt = f"""
Analyze this {language} code file and provide a structured summary:

CONTENT:
{content[:3000]}

Return ONLY a JSON object with this structure:
{{
  "file_type": "{language} code",
  "main_purpose": "brief description of file's purpose",
  "key_components": ["list of main classes/functions"],
  "dependencies": ["list of key imports/dependencies"],
  "complexity": "low/medium/high"
}}
"""
        
        response = researcher_llm.invoke([
            ("system", "You are a code analyst. Return ONLY a JSON object with the requested structure."),
            ("human", prompt)
        ])
        
        # Try to parse the response
        content_str = response.content.strip()
        if content_str.startswith('{') and content_str.endswith('}'):
            try:
                summary_data = json.loads(content_str)
                # Format as a readable summary
                summary = f"File Type: {summary_data.get('file_type', language + ' code')}\n"
                summary += f"Main Purpose: {summary_data.get('main_purpose', 'Not specified')}\n"
                summary += f"Key Components: {', '.join(summary_data.get('key_components', []))}\n"
                summary += f"Dependencies: {', '.join(summary_data.get('dependencies', []))}\n"
                summary += f"Complexity: {summary_data.get('complexity', 'unknown')}\n"
                return summary
            except:
                pass
        
        # Fallback summary
        lines = content.split('\n')
        return f"{language} code file with {len(lines)} lines. Main function appears to be related to content analysis."
    except Exception as e:
        print(f"Code summarization failed: {e}")
        return f"{language} code file. Summarization failed."


def summarize_general_document(content: str) -> str:
    """Generate structured summary for general documents"""
    try:
        # Use the HybridSummarizer for general documents
        summary = summarizer.summarize(content, "document summary", {})
        return summary
    except Exception as e:
        print(f"Document summarization failed: {e}")
        # Fallback to simple extraction
        sentences = content.split('.')[:5]
        return '. '.join(sentences) + ("..." if len(content.split('.')) > 5 else "")


def extract_content_intent_and_constraints(source_code: str, research_focus: str) -> Dict[str, Any]:
    """Extract comprehensive content intent, style preferences, and constraints from the initial prompt"""
    try:
        researcher_llm = local_llm_manager.get_researcher()
        prompt = f"""
Analyze this request and extract the complete content intent, style preferences, and constraints:

SOURCE CODE/CONTENT:
{source_code[:1500]}

RESEARCH FOCUS:
{research_focus}

Return ONLY a JSON object with this structure:
{{
  "audience": "technical developers",
  "tone": "professional but approachable",
  "post_type": "technical deep dive", // Options: tutorial, listicle, guide, deep_dive, comparison, review, overview
  "content_constraints": {{
    "word_count": 1500, // Target word count or null
    "section_count": 5, // Desired number of sections or null
    "required_phrases": ["machine learning", "neural networks"], // Key terms to include
    "exclude_topics": ["advanced mathematics"] // Topics to avoid
  }},
  "style_preferences": {{
    "formatting": "markdown", // markdown, plain_text
    "complexity_level": "intermediate", // beginner, intermediate, advanced
    "example_types": ["code", "diagrams"], // Types of examples to include
    "citation_style": "inline" // inline, footnotes, none
  }},
  "success_criteria": "The post should explain the concept clearly with practical examples."
}}
"""
        
        response = researcher_llm.invoke([
            ("system", "You are a content strategist. Extract complete content intent and constraints. Return ONLY a JSON object with the requested structure. If any field is not applicable, set it to null. For arrays, use empty arrays if not applicable."),
            ("human", prompt)
        ])
        
        # Try to parse the response
        content_str = response.content.strip()
        if content_str.startswith('{') and content_str.endswith('}'):
            try:
                intent_data = json.loads(content_str)
                return intent_data
            except Exception as parse_error:
                print(f"JSON parsing failed: {parse_error}")
                pass
        
        # Fallback with basic extraction
        return extract_basic_intent(source_code, research_focus)
    except Exception as e:
        print(f"Content intent extraction failed: {e}")
        return extract_basic_intent(source_code, research_focus)


def extract_basic_intent(source_code: str, research_focus: str) -> Dict[str, Any]:
    """Extract basic intent when advanced extraction fails"""
    combined_text = (source_code + " " + research_focus).lower()
    
    # Determine post type from keywords
    post_types = {
        "tutorial": ["tutorial", "how to", "step by step", "guide"],
        "listicle": ["listicle", "top 10", "5 ways", "best practices"],
        "deep_dive": ["deep dive", "comprehensive", "in depth", "detailed analysis"],
        "comparison": ["vs", "compared to", "comparison", "versus"],
        "review": ["review", "evaluation", "assessment"],
        "overview": ["overview", "introduction to", "basics of"]
    }
    
    post_type = "technical_article"  # default
    for ptype, keywords in post_types.items():
        if any(keyword in combined_text for keyword in keywords):
            post_type = ptype
            break
    
    # Determine audience from keywords
    audiences = {
        "Beginners": ["beginner", "basic", "intro", "getting started", "for dummies"],
        "Developers": ["developer", "programmer", "coding", "implementation"],
        "Technical Leads": ["lead", "architect", "senior", "cto", "technical lead"],
        "Researchers": ["research", "academic", "study", "paper"]
    }
    
    audience = "Developers"  # default
    for aud, keywords in audiences.items():
        if any(keyword in combined_text for keyword in keywords):
            audience = aud
            break
    
    # Determine tone from keywords
    tones = {
        "Professional": ["professional", "formal", "academic"],
        "Conversational": ["friendly", "casual", "conversational"],
        "Enthusiastic": ["exciting", "amazing", "awesome", "cool"],
        "Tutorial": ["teaching", "learning", "educational"]
    }
    
    tone = "Professional"  # default
    for t, keywords in tones.items():
        if any(keyword in combined_text for keyword in keywords):
            tone = t
            break
    
    return {
        "audience": audience,
        "tone": tone,
        "post_type": post_type,
        "content_constraints": {
            "word_count": None,
            "section_count": None,
            "required_phrases": [],
            "exclude_topics": []
        },
        "style_preferences": {
            "formatting": "markdown",
            "complexity_level": "intermediate",
            "example_types": ["code"],
            "citation_style": "inline"
        },
        "success_criteria": "Create a clear, well-structured technical post that addresses the main topic."
    }


def determine_routing_action(source_code: str, research_focus: str) -> str:
    """Determine special routing based on request nature"""
    combined_text = (source_code + " " + research_focus).lower()
    
    # Check for outline-only requests
    outline_keywords = ["outline", "structure", "plan", "just give me", "only need"]
    if any(keyword in combined_text for keyword in outline_keywords):
        # Check if it's specifically asking for an outline
        if any(word in combined_text for word in ["outline", "structure", "plan"]):
            return "route_outline"
    
    # Check for research-only requests
    research_keywords = ["research", "find", "look up", "investigate"]
    if any(keyword in combined_text for keyword in research_keywords):
        if "no blog" in combined_text or "no post" in combined_text:
            return "route_research_only"
    
    # Default routing (no special action)
    return ""