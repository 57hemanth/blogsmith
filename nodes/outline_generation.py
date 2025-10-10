from states import BlogState
from typing import Dict, Any
from config import llm
import logging

logger = logging.getLogger(__name__)

async def outline_generation_node(state: BlogState) -> Dict[str, Any]:
    """
    Generate a structured outline before writing full content.
    This improves content quality significantly.
    """
    logger.info("📋 Starting outline generation...")
    logger.info(f"   Title: {state['selected_title']}")
    
    prompt = f"""
    Create a detailed blog outline for: "{state["selected_title"]}"
    
    Website Context: {state["site_description"]}
    Target Keywords: {", ".join(state.get("keywords", [])[:5])}
    
    Competitor Insights:
    {state.get("competitor_summary", "")}
    
    Create an outline with:
    - Introduction hook
    - 4-6 main sections with subpoints
    - Key takeaways/conclusion
    - Suggested word count per section
    
    Make it comprehensive and SEO-friendly.
    """
    
    response = await llm.ainvoke([
        {"role": "system", "content": "You are a professional content strategist."},
        {"role": "user", "content": prompt}
    ])
    
    logger.info(f"✅ Outline generated ({len(response.content)} characters)")
    
    return {
        "blog_outline": response.content,
        "current_step": "outline_generation_complete"
    }
