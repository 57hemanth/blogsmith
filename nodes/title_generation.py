from states import BlogState
from typing import Dict, Any
from config import llm
import json
import logging
import re

logger = logging.getLogger(__name__)

async def title_generation_node(state: BlogState) -> Dict[str, Any]:
    """
    Generate multiple blog title options.
    """
    logger.info("📝 Starting title generation...")
    
    existing_titles = [blog["title"] for blog in state.get("existing_blogs", [])]
    keywords = state.get("keywords", [])
    
    prompt = f"""
    Generate 10 compelling blog titles for our website.
    
    Website: {state["site_title"]}
    Description: {state["site_description"]}
    
    Target Keywords: {", ".join(keywords[:5]) if keywords else "general topics"}
    
    Competitor Insights:
    {state.get("competitor_summary", "")}
    
    Existing Blog Titles (AVOID DUPLICATES):
    {existing_titles if existing_titles else "None"}
    
    Requirements:
    - SEO-optimized
    - Engaging and click-worthy
    - Include at least one target keyword
    - Different from existing titles
    - Various formats (how-to, listicles, guides, etc.)
    
    Return ONLY a JSON array of titles, no other text or markdown.
    Example: ["title1", "title2", "title3"]
    """
    
    try:
        response = await llm.ainvoke([
            {"role": "system", "content": "You are a content marketing expert. Always return valid JSON arrays only."},
            {"role": "user", "content": prompt}
        ])
        
        content = response.content.strip()
        logger.debug(f"Raw LLM response: {content[:200]}")
        
        # Extract JSON from markdown code blocks if present
        if "```" in content:
            match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', content, re.DOTALL)
            if match:
                content = match.group(1)
            else:
                match = re.search(r'\[.*?\]', content, re.DOTALL)
                if match:
                    content = match.group(0)
        
        titles = json.loads(content)
        
        if not isinstance(titles, list):
            raise ValueError("Response is not a list")
        
        logger.info(f"✅ Generated {len(titles)} title options")
        for i, title in enumerate(titles[:3], 1):
            logger.info(f"   {i}. {title}")
        
        return {
            "titles": titles,
            "current_step": "title_generation_complete"
        }
        
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"❌ Failed to parse titles from LLM response: {e}")
        logger.debug(f"Response content was: {content}")
        
        # Fallback titles
        primary_keyword = keywords[0] if keywords else state["site_title"]
        fallback_titles = [
            f"The Ultimate Guide to {primary_keyword}",
            f"10 Best {primary_keyword} Tips for Beginners",
            f"How to Master {primary_keyword} in 2024",
            f"Everything You Need to Know About {primary_keyword}",
            f"{primary_keyword}: A Complete Guide",
            f"Top {primary_keyword} Strategies That Actually Work",
            f"Beginner's Guide to {primary_keyword}",
            f"{primary_keyword} 101: Getting Started",
            f"The Complete {primary_keyword} Tutorial",
            f"Essential {primary_keyword} Tips and Tricks"
        ]
        
        logger.warning(f"⚠️  Using fallback titles")
        
        return {
            "titles": fallback_titles,
            "current_step": "title_generation_complete_with_fallback",
            "error": f"Failed to generate titles from LLM: {str(e)}"
        }
