import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime


def render_analytics(result_state: dict):
    """Render comprehensive generation analytics with visualizations"""
    st.header("📊 Generation Analytics")

    # Top-level KPIs
    render_kpi_cards(result_state)
    
    st.divider()
    
    # Main analytics sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Token Usage",
        "🔬 Research Insights",
        "📝 Content Metrics",
        "⚡ Performance"
    ])
    
    with tab1:
        render_token_analytics(result_state)
    
    with tab2:
        render_research_analytics(result_state)
    
    with tab3:
        render_content_analytics(result_state)
    
    with tab4:
        render_performance_analytics(result_state)


def render_kpi_cards(result_state: dict):
    """Render top-level KPI cards"""
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Token usage
    usage = result_state.get("token_usage", {}) or {}
    total_tokens = sum(usage.values())
    
    # Content stats
    sections = result_state.get("sections") or []
    drafts = result_state.get("section_drafts") or {}
    final_content = result_state.get("research_context", {}).get("completion_summary", {}).get("final_content", "")
    word_count = len(final_content.split()) if final_content else 0
    
    # Research stats
    research_context = result_state.get("research_context", {}) or {}
    by_source = research_context.get("by_source", {})
    total_sources = sum(len(v) if isinstance(v, list) else 1 for v in by_source.values())
    
    # Plagiarism stats
    plagiarism_checks = result_state.get("plagiarism_checks", {}) or {}
    avg_originality = 0
    if plagiarism_checks:
        scores = [check.get("originality_score", 0) for check in plagiarism_checks.values()]
        avg_originality = sum(scores) / len(scores) if scores else 0
    
    # Credits remaining
    credits = result_state.get("free_tier_credits", 100)
    
    with col1:
        st.metric("Total Tokens", f"{total_tokens:,}", help="Total tokens used across all models")
    
    with col2:
        st.metric("Word Count", f"{word_count:,}", help="Total words in final blog post")
    
    with col3:
        st.metric("Sections", len(sections), help="Number of sections generated")
    
    with col4:
        st.metric("Research Sources", total_sources, help="Total research results collected")
    
    with col5:
        delta_color = "normal" if avg_originality >= 80 else "inverse"
        st.metric(
            "Avg Originality", 
            f"{avg_originality:.1f}%", 
            delta=f"{avg_originality - 80:.1f}%" if avg_originality > 0 else None,
            delta_color=delta_color,
            help="Average originality score across all sections"
        )


def render_token_analytics(result_state: dict):
    """Display detailed token usage analytics with visualizations"""
    usage = result_state.get("token_usage", {}) or {}
    
    if not usage:
        st.info("No token usage recorded.")
        return
    
    total = sum(usage.values())
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Pie chart of token distribution
        fig = go.Figure(data=[go.Pie(
            labels=list(usage.keys()),
            values=list(usage.values()),
            hole=0.4,
            marker=dict(colors=px.colors.qualitative.Set3)
        )])
        
        fig.update_layout(
            title="Token Distribution by Model",
            height=400,
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Token Breakdown")
        st.metric("Total Tokens", f"{total:,}")
        
        # Estimated cost (assuming $0.001 per 1K tokens as average)
        est_cost = (total / 1000) * 0.001
        st.metric("Est. Cost", f"${est_cost:.4f}")
        
        st.divider()
        
        # Per-model breakdown
        for model, tokens in sorted(usage.items(), key=lambda x: x[1], reverse=True):
            percentage = (tokens / total * 100) if total > 0 else 0
            st.write(f"**{model}**")
            st.progress(percentage / 100)
            st.caption(f"{tokens:,} tokens ({percentage:.1f}%)")
    
    # Bar chart comparison
    st.subheader("Token Usage Comparison")
    fig_bar = go.Figure(data=[go.Bar(
        x=list(usage.keys()),
        y=list(usage.values()),
        marker=dict(color=px.colors.qualitative.Pastel),
        text=list(usage.values()),
        textposition='auto'
    )])
    
    fig_bar.update_layout(
        title="Tokens per Model",
        xaxis_title="Model",
        yaxis_title="Tokens",
        height=350
    )
    
    st.plotly_chart(fig_bar, use_container_width=True)


def render_research_analytics(result_state: dict):
    """Display detailed research analytics with visualizations"""
    research_context = result_state.get("research_context", {}) or {}
    by_source = research_context.get("by_source", {})
    
    if not by_source:
        st.info("No research data available.")
        return
    
    # Count items per source
    source_counts = {}
    for source, data in by_source.items():
        if isinstance(data, list):
            source_counts[source.title()] = len(data)
        else:
            source_counts[source.title()] = 1
    
    if not source_counts:
        st.info("No research sources found.")
        return
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Research Summary")
        total_results = sum(source_counts.values())
        st.metric("Total Results", total_results)
        
        st.divider()
        
        # Source breakdown
        for source, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True):
            st.write(f"**{source}**")
            st.progress(count / total_results if total_results > 0 else 0)
            st.caption(f"{count} result(s)")
    
    with col2:
        # Bar chart of research sources
        fig = go.Figure(data=[go.Bar(
            x=list(source_counts.keys()),
            y=list(source_counts.values()),
            marker=dict(
                color=list(source_counts.values()),
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Results")
            ),
            text=list(source_counts.values()),
            textposition='auto'
        )])
        
        fig.update_layout(
            title="Research Results by Source",
            xaxis_title="Source",
            yaxis_title="Number of Results",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Research quality insights
    st.subheader("Research Quality Insights")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        synthesis_type = research_context.get("synthesis_type", "general")
        st.metric("Synthesis Type", synthesis_type.title())
    
    with col2:
        has_intro = "introduction" in research_context
        st.metric("Introduction", "✅ Generated" if has_intro else "❌ Missing")
    
    with col3:
        key_insights = research_context.get("key_insights", [])
        st.metric("Key Insights", len(key_insights) if isinstance(key_insights, list) else 0)


def render_content_analytics(result_state: dict):
    """Display detailed content analytics with visualizations"""
    sections = result_state.get("sections") or []
    drafts = result_state.get("section_drafts") or {}
    citations = result_state.get("citations", {}) or {}
    revision_history = result_state.get("revision_history", {}) or {}
    
    if not sections:
        st.info("No content generated yet.")
        return
    
    # Calculate metrics
    section_word_counts = {}
    for section in sections:
        section_id = section.get("id")
        content = drafts.get(section_id, "")
        word_count = len(content.split()) if content else 0
        section_word_counts[section.get("title", f"Section {section_id}")] = word_count
    
    total_words = sum(section_word_counts.values())
    avg_words_per_section = total_words / len(sections) if sections else 0
    
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Sections", len(sections))
    
    with col2:
        drafted = len([k for k, v in drafts.items() if (v or '').strip()])
        st.metric("Drafted", drafted)
    
    with col3:
        total_citations = sum(len(v) if isinstance(v, list) else 1 for v in citations.values())
        st.metric("Citations", total_citations)
    
    with col4:
        revised = len([k for k, v in revision_history.items() if v])
        st.metric("Revised", revised)
    
    st.divider()
    
    # Word count distribution
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if section_word_counts:
            fig = go.Figure(data=[go.Bar(
                x=list(section_word_counts.keys()),
                y=list(section_word_counts.values()),
                marker=dict(
                    color=list(section_word_counts.values()),
                    colorscale='Blues',
                    showscale=True,
                    colorbar=dict(title="Words")
                ),
                text=list(section_word_counts.values()),
                textposition='auto'
            )])
            
            fig.update_layout(
                title="Word Count per Section",
                xaxis_title="Section",
                yaxis_title="Words",
                height=400,
                xaxis_tickangle=-45
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Content Summary")
        st.metric("Total Words", f"{total_words:,}")
        st.metric("Avg Words/Section", f"{avg_words_per_section:.0f}")
        
        # Reading time estimate (avg 200 words/min)
        reading_time = total_words / 200
        st.metric("Est. Reading Time", f"{reading_time:.1f} min")
    
    # Section details table
    st.subheader("Section Details")
    
    section_data = []
    for section in sections:
        section_id = section.get("id")
        title = section.get("title", f"Section {section_id}")
        content = drafts.get(section_id, "")
        word_count = len(content.split()) if content else 0
        has_citations = section_id in citations
        has_revisions = section_id in revision_history and revision_history[section_id]
        
        section_data.append({
            "Section": title,
            "Words": word_count,
            "Citations": "✅" if has_citations else "❌",
            "Revised": "✅" if has_revisions else "❌",
            "Status": "✅ Complete" if content else "⏳ Pending"
        })
    
    st.dataframe(section_data, use_container_width=True, hide_index=True)


def render_performance_analytics(result_state: dict):
    """Display workflow performance analytics"""
    completion_summary = result_state.get("research_context", {}).get("completion_summary", {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Workflow Metrics")
        
        total_sections = completion_summary.get("total_sections", 0)
        checked_sections = completion_summary.get("checked_sections", 0)
        revised_sections = completion_summary.get("sections_with_revisions", 0)
        
        st.metric("Total Sections", total_sections)
        st.metric("Plagiarism Checked", checked_sections)
        st.metric("Revised Sections", revised_sections)
        
        # Efficiency score
        if total_sections > 0:
            efficiency = ((total_sections - revised_sections) / total_sections) * 100
            st.metric(
                "First-Pass Success",
                f"{efficiency:.1f}%",
                help="Percentage of sections that passed without revision"
            )
    
    with col2:
        st.subheader("Resource Usage")
        
        total_tokens = completion_summary.get("total_tokens", 0)
        credits_remaining = completion_summary.get("remaining_credits", 100)
        credits_used = 100 - credits_remaining
        
        st.metric("Total Tokens", f"{total_tokens:,}")
        st.metric("Credits Used", credits_used)
        st.metric("Credits Remaining", credits_remaining)
        
        # Progress bar for credits
        st.progress(credits_remaining / 100)
    
    st.divider()
    
    # Plagiarism check results
    st.subheader("Plagiarism Check Results")
    
    plagiarism_checks = result_state.get("plagiarism_checks", {}) or {}
    
    if plagiarism_checks:
        originality_scores = []
        section_names = []
        
        sections = result_state.get("sections", [])
        section_map = {s.get("id"): s.get("title", f"Section {s.get('id')}") for s in sections}
        
        for section_id, check in plagiarism_checks.items():
            score = check.get("originality_score", 0)
            originality_scores.append(score)
            section_names.append(section_map.get(section_id, section_id))
        
        # Gauge chart for average originality
        avg_originality = sum(originality_scores) / len(originality_scores) if originality_scores else 0
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=avg_originality,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Average Originality Score"},
            delta={'reference': 80, 'increasing': {'color': "green"}},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 60], 'color': "lightcoral"},
                    {'range': [60, 80], 'color': "lightyellow"},
                    {'range': [80, 100], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 80
                }
            }
        ))
        
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
        
        # Originality by section
        if len(originality_scores) > 1:
            fig_bar = go.Figure(data=[go.Bar(
                x=section_names,
                y=originality_scores,
                marker=dict(
                    color=originality_scores,
                    colorscale='RdYlGn',
                    cmin=0,
                    cmax=100,
                    showscale=True,
                    colorbar=dict(title="Score")
                ),
                text=[f"{s:.1f}%" for s in originality_scores],
                textposition='auto'
            )])
            
            fig_bar.update_layout(
                title="Originality Score by Section",
                xaxis_title="Section",
                yaxis_title="Originality (%)",
                height=350,
                xaxis_tickangle=-45
            )
            
            # Add threshold line
            fig_bar.add_hline(y=80, line_dash="dash", line_color="red", annotation_text="Threshold (80%)")
            
            st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No plagiarism checks performed yet.")