from states import BlogState
from typing import Dict, Any
from config import llm
import re
import logging

logger = logging.getLogger(__name__)


def strip_ai_preamble(content: str) -> str:
    """Remove common AI preamble and trailing commentary from generated content."""
    cleaned = content.strip()

    # Strip leading preamble patterns
    preamble_patterns = [
        r'^(?:Here\s+is|Here\'s|Below\s+is).*?(?:blog|article|post|content).*?[:\n]+\s*',
        r'^(?:Sure|Certainly|Of course|Absolutely).*?[:\n]+\s*',
        r'^(?:I\'ve|I have).*?(?:written|created|generated|prepared).*?[:\n]+\s*',
    ]
    for pattern in preamble_patterns:
        cleaned = re.sub(pattern, '', cleaned, count=1, flags=re.IGNORECASE | re.DOTALL)

    # Strip trailing AI commentary
    trailing_patterns = [
        r'\n---\s*\n(?:I hope|Let me know|Feel free|This article|This blog|If you).*$',
        r'\n\n(?:I hope|Let me know|Feel free|This article|This blog|If you).*$',
    ]
    for pattern in trailing_patterns:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE | re.DOTALL)

    return cleaned.strip()


async def content_generation_node(state: BlogState) -> Dict[str, Any]:
    """
    Generate SEO-optimized blog content following Yoast SEO Premium guidelines.
    """
    logger.info("Starting content generation...")
    logger.info(f"   Title: {state['selected_title']}")

    target_keyword = state.get("target_keyword", "")
    secondary_keywords = state.get("secondary_keywords", [])

    system_prompt = (
        "You are a Senior SEO Content Specialist and Professional Copywriter. "
        "You write content optimized for Yoast SEO Premium (targeting 90%+ Green Light score). "
        "You NEVER include preamble text like 'Here is the blog', 'Here is your article', "
        "'Sure, here you go', or any introductory commentary. "
        "You start directly with the blog content in Markdown format."
    )

    prompt = f"""
    Write a complete SEO-optimized blog post following the outline EXACTLY.

    Title: {state["selected_title"]}
    Target Keyword: {target_keyword}
    Secondary Keywords: {", ".join(secondary_keywords)}

    Outline:
    {state.get("blog_outline", "")}

    Website Context:
    - Site: {state["site_title"]} ({state.get("site_url", "")})
    - Description: {state["site_description"]}
    - Additional Keywords: {", ".join(state.get("keywords", []))}
    - Competitor Insights: {state.get("competitor_summary", "")}

    === SEO Writing Rules (Yoast SEO Premium Green Light) ===

    WORD COUNT: 1,300-1,500 words. Do NOT exceed 1,500 words.

    KEYWORD USAGE:
    - Target keyword "{target_keyword}" must appear in: H1, first paragraph (within first 100 words), at least 2 H2 headings, and conclusion
    - Keyword density: 1-1.5%
    - Each secondary keyword ({", ".join(secondary_keywords)}) must appear at least once naturally

    READABILITY (Critical):
    - Flesch Reading Ease: 55-70
    - Passive voice: less than 10% of sentences
    - Transition words: at least 35% of sentences must use transition words (e.g., "however", "therefore", "in addition", "moreover", "as a result", "for example", "consequently")
    - At least 80% of sentences must be under 20 words
    - Paragraphs: 2-4 sentences each, max 120 words per paragraph
    - NEVER start 3 consecutive sentences with the same word

    STRUCTURE:
    - Use H2 for main sections, H3 for subsections
    - Include bullet points and numbered lists where appropriate
    - Bold key phrases containing target keyword
    - Short, scannable paragraphs

    LINKS:
    - Include 1 internal link to: {state.get("site_url", "")}
    - Include 1 external link to an authoritative source (relevant to the topic)

    TONE:
    - Professional yet conversational and accessible
    - Actionable advice with practical examples
    - Localize for Indian context where relevant (INR pricing, local platforms like Razorpay/Paytm, TRAI compliance, GST references)

    BLOG STRUCTURE (follow this order):
    1. H1: Blog title with "{target_keyword}"
    2. Introduction: Hook, include "{target_keyword}" in first 50 words, mention {", ".join(secondary_keywords)}
    3. H2/H3 sections as per the outline
    4. H2: FAQ section with 3-5 questions as H3s and concise answers
    5. H2: Conclusion with summary of key benefits and strong CTA including "{target_keyword}"

    IMPORTANT: Output ONLY the blog post in Markdown format. Start directly with the H1 heading. No preamble, no commentary, no introduction text before or after the article.
    """

    response = await llm.ainvoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ])

    # Clean AI preamble/trailing text
    content = strip_ai_preamble(response.content)

    word_count = len(content.split())
    logger.info(f"Content generated: {word_count} words, {len(content)} characters")

    return {
        "blog_content": content,
        "current_step": "content_generation_complete"
    }
