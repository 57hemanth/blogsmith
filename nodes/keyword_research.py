from states import BlogState
from typing import Dict, Any
from config import llm
import json

async def keyword_research_node(state: BlogState) -> Dict[str, Any]:
    """
    Generate relevant keywords based on site info and competitor research.
    """

    prompt = f"""
    You are an SEO expert. Generate 15-20 relevant keywords for a blog.
    
    Website: {state["site_title"]}
    Description: {state["site_description"]}
    
    Competitor Insights:
    {state.get("competitor_summary", "No competitor data")}
    
    Consider:
    - Primary keywords (high search volume)
    - Long-tail keywords (specific, lower competition)
    - LSI keywords (semantically related)
    - Keywords from competitor analysis
    
    Return ONLY a JSON array of keywords, no other text.
    Example: ["keyword1", "keyword2", ...]
    """
    
    response = await llm.ainvoke([
        {"role": "system", "content": "You are an SEO keyword research expert."},
        {"role": "user", "content": prompt}
    ])
    
    # Parse keywords (you might want to use structured output)
    
    keywords = json.loads(response.content)
    
    return {
        "keywords": keywords,
        "current_step": "keyword_research_complete"
    }
