from states import BlogState
from typing import Dict, Any
from config import llm
import json
import logging
import re

logger = logging.getLogger(__name__)

async def title_generation_node(state: BlogState) -> Dict[str, Any]:
    """
    Generate multiple SEO-optimized blog title options.
    """
    logger.info("Starting title generation...")

    existing_titles = [blog["title"] for blog in state.get("existing_blogs", [])]
    keywords = state.get("keywords", [])
    target_keyword = state.get("target_keyword", "")
    secondary_keywords = state.get("secondary_keywords", [])

    prompt = f"""
    Generate 10 SEO-optimized blog titles.

    Website: {state["site_title"]}
    Description: {state["site_description"]}
    Target Keyword: {target_keyword}
    Secondary Keywords: {", ".join(secondary_keywords)}
    Generated Keywords: {", ".join(keywords[:5]) if keywords else "general topics"}

    Title Format Pattern:
    {target_keyword}: How [audience] Can [benefit] with {", ".join(secondary_keywords[:2]) if secondary_keywords else "[related topics]"}

    Requirements:
    - Every title MUST contain the target keyword "{target_keyword}"
    - Follow the pattern above or close variations
    - SEO-optimized for search engines
    - Engaging and click-worthy
    - Different from existing titles: {existing_titles if existing_titles else "None"}
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

        logger.info(f"Generated {len(titles)} title options")
        for i, title in enumerate(titles[:3], 1):
            logger.info(f"   {i}. {title}")

        return {
            "titles": titles,
            "current_step": "title_generation_complete"
        }

    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Failed to parse titles from LLM response: {e}")
        logger.debug(f"Response content was: {content}")

        # Fallback titles using target keyword
        kw = target_keyword if target_keyword else (keywords[0] if keywords else state["site_title"])
        sec = ", ".join(secondary_keywords[:2]) if secondary_keywords else "Best Practices"
        fallback_titles = [
            f"{kw}: How Indian Startups Can Boost Sales with {sec}",
            f"The Ultimate Guide to {kw} for Startups",
            f"10 Best {kw} Tips for Beginners",
            f"How to Master {kw} in 2025",
            f"Everything You Need to Know About {kw}",
            f"{kw}: A Complete Guide for Growing Businesses",
            f"Top {kw} Strategies That Actually Work",
            f"Beginner's Guide to {kw} and {sec}",
            f"{kw} 101: Getting Started",
            f"Essential {kw} Tips and Tricks"
        ]

        logger.warning("Using fallback titles")

        return {
            "titles": fallback_titles,
            "current_step": "title_generation_complete_with_fallback",
            "error": f"Failed to generate titles from LLM: {str(e)}"
        }
