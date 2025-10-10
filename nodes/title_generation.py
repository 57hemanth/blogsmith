from states import BlogState
from typing import Dict, Any
from config import llm
import json

async def title_generation_node(state: BlogState) -> Dict[str, Any]:
    """
    Generate multiple blog title options.
    """
    
    existing_titles = [blog["title"] for blog in state.get("existing_blogs", [])]
    
    prompt = f"""
    Generate 10 compelling blog titles for our website.
    
    Website: {state["site_title"]}
    Description: {state["site_description"]}
    
    Target Keywords: {", ".join(state["keywords"][:5])}
    
    Competitor Insights:
    {state.get("competitor_summary", "")}
    
    Existing Blog Titles (AVOID DUPLICATES):
    {existing_titles}
    
    Requirements:
    - SEO-optimized
    - Engaging and click-worthy
    - Include at least one target keyword
    - Different from existing titles
    - Various formats (how-to, listicles, guides, etc.)
    
    Return ONLY a JSON array of titles, no other text.
    Example: ["title1", "title2", ...]
    """
    
    response = await llm.ainvoke([
        {"role": "system", "content": "You are a content marketing expert."},
        {"role": "user", "content": prompt}
    ])
    
    titles = json.loads(response.content)
    
    return {
        "titles": titles,
        "current_step": "title_generation_complete"
    }
