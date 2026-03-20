from states import BlogState
from typing import Dict, Any
from config import llm
import logging

logger = logging.getLogger(__name__)

async def outline_generation_node(state: BlogState) -> Dict[str, Any]:
    """
    Generate a structured SEO-optimized outline before writing full content.
    """
    logger.info("Starting outline generation...")
    logger.info(f"   Title: {state['selected_title']}")

    target_keyword = state.get("target_keyword", "")
    secondary_keywords = state.get("secondary_keywords", [])

    prompt = f"""
    Create a detailed SEO-optimized blog outline for: "{state["selected_title"]}"

    Website Context: {state["site_description"]}
    Target Keyword: {target_keyword}
    Secondary Keywords: {", ".join(secondary_keywords)}
    Additional Keywords: {", ".join(state.get("keywords", [])[:5])}

    Competitor Insights:
    {state.get("competitor_summary", "")}

    Required Blog Structure (follow this exactly):

    1. H1: The blog title (must contain target keyword "{target_keyword}")

    2. Introduction (2-3 paragraphs):
       - Hook the reader immediately
       - Include "{target_keyword}" within the first 50 words
       - Mention secondary keywords: {", ".join(secondary_keywords)}
       - State what readers will learn

    3. H2: Why {target_keyword} is Essential for Indian Startups
       - H3: Common {target_keyword} Mistakes
       - H3: Tools for Effective {target_keyword} (note: include 1 internal link and 1 external authoritative link here)

    4. H2: Integrating {", ".join(secondary_keywords)} to Maximize Engagement
       - H3: Choosing the Right {", ".join(secondary_keywords)} Platform
       - H3: Best Practices for {", ".join(secondary_keywords)}

    5. H2: Combining {target_keyword} and {", ".join(secondary_keywords)} for Maximum Impact

    6. H2: Conclusion
       - Summarize key benefits
       - Include strong call-to-action (CTA)
       - Include "{target_keyword}"

    7. H2: FAQ (Optional)
       - 3-5 frequently asked questions covering "{target_keyword}" and "{", ".join(secondary_keywords)}"
       - Each question as an H3 with concise answers

    Additional Requirements:
    - Target word count: 1,300-1,500 words total
    - Note suggested word count per section
    - Mark where internal link (to {state.get("site_url", "the site")}) and external authoritative link should be placed
    """

    response = await llm.ainvoke([
        {"role": "system", "content": "You are a professional SEO content strategist."},
        {"role": "user", "content": prompt}
    ])

    logger.info(f"Outline generated ({len(response.content)} characters)")

    return {
        "blog_outline": response.content,
        "current_step": "outline_generation_complete"
    }
