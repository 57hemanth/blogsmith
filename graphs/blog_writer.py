from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from states import BlogState
from nodes import (
    competitor_research_node, 
    keyword_research_node, 
    title_generation_node, 
    title_selection_node, 
    outline_generation_node, 
    content_generation_node, 
    image_generation_node
)
from typing import List, Dict, Literal
import logging

logger = logging.getLogger(__name__)


def should_skip_competitor_research(state: BlogState) -> Literal["keyword_research", "competitor_research"]:
    """Conditional edge function: Skip competitor research if no URLs provided"""
    if not state.get("competitors_urls") or len(state["competitors_urls"]) == 0:
        logger.info("⏭️  No competitors provided, skipping competitor research")
        return "keyword_research"
    logger.info(f"🔍 Starting competitor research for {len(state['competitors_urls'])} competitors")
    return "competitor_research"


def create_blog_writer_graph():
    """
    Create the blog writing workflow graph with checkpointing.
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

    # Conditional routing from START
    workflow.add_conditional_edges(
        START,
        should_skip_competitor_research,
        {
            "competitor_research": "competitor_research",
            "keyword_research": "keyword_research"
        }
    )
    
    # Linear workflow
    workflow.add_edge("competitor_research", "keyword_research")
    workflow.add_edge("keyword_research", "title_generation")
    workflow.add_edge("title_generation", "title_selection")
    workflow.add_edge("title_selection", "outline_generation")
    workflow.add_edge("outline_generation", "content_generation")
    workflow.add_edge("content_generation", "image_generation")
    workflow.add_edge("image_generation", END)

    # Compile with SQLite checkpointer for persistence
    checkpointer = SqliteSaver.from_conn_string("checkpoints.db")
    return workflow.compile(checkpointer=checkpointer)


# Export the compiled graph for LangGraph Studio
graph = create_blog_writer_graph()

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