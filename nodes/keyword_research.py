from states import BlogState
from typing import Dict, Any
from config import llm
import json
import logging
import re

logger = logging.getLogger(__name__)

async def keyword_research_node(state: BlogState) -> Dict[str, Any]:
    """
    Generate relevant keywords based on site info and competitor research.
    """
    logger.info("🔑 Starting keyword research...")

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
    
    Return ONLY a JSON array of keywords, no other text or markdown.
    Example: ["keyword1", "keyword2", "keyword3"]
    """
    
    try:
        response = await llm.ainvoke([
            {"role": "system", "content": "You are an SEO keyword research expert. Always return valid JSON arrays only."},
            {"role": "user", "content": prompt}
        ])
        
        content = response.content.strip()
        logger.debug(f"Raw LLM response: {content[:200]}")
        
        # Extract JSON from markdown code blocks if present
        if "```" in content:
            # Extract content between code blocks
            match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', content, re.DOTALL)
            if match:
                content = match.group(1)
            else:
                # Try to find JSON array anywhere in the response
                match = re.search(r'\[.*?\]', content, re.DOTALL)
                if match:
                    content = match.group(0)
        
        # Parse JSON
        keywords = json.loads(content)
        
        if not isinstance(keywords, list):
            raise ValueError("Response is not a list")
        
        logger.info(f"✅ Generated {len(keywords)} keywords: {', '.join(keywords[:5])}...")
        
        return {
            "keywords": keywords,
            "current_step": "keyword_research_complete"
        }
        
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"❌ Failed to parse keywords from LLM response: {e}")
        logger.debug(f"Response content was: {content}")
        
        # Fallback: generate keywords from the site description
        site_words = state["site_description"].lower().split()
        fallback_keywords = [
            state["site_title"].lower(),
            "blog",
            "guide",
            "tips"
        ] + [word for word in site_words if len(word) > 4][:10]
        
        logger.warning(f"⚠️  Using fallback keywords: {fallback_keywords}")
        
        return {
            "keywords": fallback_keywords[:15],
            "current_step": "keyword_research_complete_with_fallback",
            "error": f"Failed to generate keywords from LLM: {str(e)}"
        }
