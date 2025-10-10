from states import BlogState
from typing import Dict, Any
from config import llm

async def title_selection_node(state: BlogState) -> Dict[str, Any]:
    """
    Select the best title from generated options.
    You can make this intelligent or simple.
    """
    
    # Option 1: Let LLM choose the best one
    prompt = f"""
    Select the BEST title from these options based on:
    - SEO potential
    - Reader engagement
    - Uniqueness
    - Relevance to: {state["site_description"]}
    
    Titles:
    {chr(10).join([f"{i+1}. {title}" for i, title in enumerate(state["titles"])])}
    
    Return ONLY the selected title text, nothing else.
    """
    
    response = await llm.ainvoke([
        {"role": "system", "content": "You are a content strategist."},
        {"role": "user", "content": prompt}
    ])
    
    selected_title = response.content.strip().strip('"')
    
    # Option 2: Simple approach - just pick the first one
    # selected_title = state["titles"][0]
    
    return {
        "selected_title": selected_title,
        "current_step": "title_selection_complete"
    }
