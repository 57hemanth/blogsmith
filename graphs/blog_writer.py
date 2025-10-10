from langgraph.graph import StateGraph, START, END
from states import BlogState
from nodes import competitor_research_node, keyword_research_node, title_generation_node, title_selection_node, outline_generation_node, content_generation_node, image_generation_node
from typing import List, Dict

def should_skip_competitor_research(state: BlogState) -> str:
    """Conditional edge function"""
    if not state.get("competitors_urls") or len(state["competitors_urls"]) == 0:
        return "keyword_research"
    return "competitor_research"

def create_blog_writer_graph():
    """
    Create the blog writing workflow graph.
    """
    workflow = StateGraph(BlogState)

    # Add nodes
    workflow.add_node("competitor_research", competitor_research_node)
    workflow.add_node("keyword_research", keyword_research_node)
    workflow.add_node("title_generation", title_generation_node)
    workflow.add_node("title_selection", title_selection_node)
    workflow.add_node("outline_generation", outline_generation_node)
    workflow.add_node("content_generation", content_generation_node)
    workflow.add_node("image_generation", image_generation_node)

    # Add edges
    workflow.add_edge(START, "competitor_research")
    workflow.add_conditional_edges(
        "competitor_research",
        should_skip_competitor_research,
        {"keyword_research": "keyword_research", "competitor_research": "competitor_research"}
    )
    workflow.add_edge("competitor_research", END)
    workflow.add_edge("keyword_research", END)
    workflow.add_edge("content_generation", END)

    return workflow.compile()

async def run_blog_writer(
    site_url: str,
    site_title: str,
    site_description: str,
    existing_blogs: List[Dict[str, str]],
    competitors_urls: List[str]
):
    """
    Run the blog writer agent.
    """
    graph = create_blog_writer_graph()
    
    initial_state = {
        "site_url": site_url,
        "site_title": site_title,
        "site_description": site_description,
        "existing_blogs": existing_blogs,
        "competitors_urls": competitors_urls,
        "messages": []
    }
    
    result = await graph.ainvoke(initial_state)
    
    return result