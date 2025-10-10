from states import BlogState
from typing import Dict, Any
from config import llm
import logging

logger = logging.getLogger(__name__)

async def title_selection_node(state: BlogState) -> Dict[str, Any]:
    """
    Select the best title from generated options.
    """
    logger.info("🎯 Starting title selection...")
    
    titles = state.get("titles", [])
    
    if not titles:
        logger.error("❌ No titles available for selection")
        return {
            "selected_title": f"Guide to {state['site_title']}",
            "current_step": "title_selection_complete_with_fallback",
            "error": "No titles available"
        }
    
    try:
        prompt = f"""
        Select the BEST title from these options based on:
        - SEO potential
        - Reader engagement
        - Uniqueness
        - Relevance to: {state["site_description"]}
        
        Titles:
        {chr(10).join([f"{i+1}. {title}" for i, title in enumerate(titles)])}
        
        Return ONLY the selected title text, nothing else. No quotes, no explanations.
        """
        
        response = await llm.ainvoke([
            {"role": "system", "content": "You are a content strategist. Return only the selected title."},
            {"role": "user", "content": prompt}
        ])
        
        selected_title = response.content.strip().strip('"').strip("'")
        
        # Verify the selected title is actually in our list
        if selected_title not in titles:
            logger.warning(f"⚠️  LLM selected title not in list, using first title")
            selected_title = titles[0]
        
        logger.info(f"✅ Selected title: {selected_title}")
        
        return {
            "selected_title": selected_title,
            "current_step": "title_selection_complete"
        }
        
    except Exception as e:
        logger.error(f"❌ Title selection failed: {e}")
        selected_title = titles[0]
        logger.warning(f"⚠️  Using first title as fallback: {selected_title}")
        
        return {
            "selected_title": selected_title,
            "current_step": "title_selection_complete_with_fallback",
            "error": str(e)
        }
