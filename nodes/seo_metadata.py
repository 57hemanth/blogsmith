from states import BlogState
from typing import Dict, Any
from config import llm
import json
import re
import logging

logger = logging.getLogger(__name__)


async def seo_metadata_node(state: BlogState) -> Dict[str, Any]:
    """
    Generate SEO metadata: tags, meta description, URL slug, and image alt text.
    """
    logger.info("Starting SEO metadata generation...")

    target_keyword = state.get("target_keyword", "")
    secondary_keywords = state.get("secondary_keywords", [])

    prompt = f"""
    Generate SEO metadata for this blog post.

    Title: {state["selected_title"]}
    Target Keyword: {target_keyword}
    Secondary Keywords: {", ".join(secondary_keywords)}
    Content (first 500 chars): {state.get("blog_content", "")[:500]}

    Return a JSON object with exactly these fields:
    {{
        "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
        "meta_description": "140-155 character meta description including target keyword and a strong CTA",
        "url_slug": "lowercase-hyphenated-slug-with-keyword",
        "image_alt_text": "descriptive alt text containing {target_keyword}"
    }}

    Rules:
    - tags: exactly 5 SEO-relevant tags related to "{target_keyword}" and "{", ".join(secondary_keywords)}"
    - meta_description: MUST be 140-155 characters, MUST include "{target_keyword}", should be compelling with a CTA for search results
    - url_slug: lowercase, hyphenated, no special characters, must include main words from "{target_keyword}", max 60 characters
    - image_alt_text: descriptive, includes "{target_keyword}", suitable for screen readers, max 125 characters

    Return ONLY the JSON object, no other text or markdown.
    """

    try:
        response = await llm.ainvoke([
            {"role": "system", "content": "You are an SEO metadata specialist. Return only valid JSON."},
            {"role": "user", "content": prompt}
        ])

        content = response.content.strip()
        logger.debug(f"Raw LLM response: {content[:200]}")

        # Extract JSON from markdown code blocks if present
        if "```" in content:
            match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
            if match:
                content = match.group(1)
            else:
                match = re.search(r'\{.*\}', content, re.DOTALL)
                if match:
                    content = match.group(0)

        metadata = json.loads(content)

        tags = metadata.get("tags", [])[:5]
        meta_description = metadata.get("meta_description", "")[:155]
        url_slug = metadata.get("url_slug", "")
        image_alt_text = metadata.get("image_alt_text", "")[:125]

        logger.info(f"Tags: {tags}")
        logger.info(f"Meta description ({len(meta_description)} chars): {meta_description}")
        logger.info(f"URL slug: {url_slug}")
        logger.info(f"Image alt text: {image_alt_text}")

        return {
            "tags": tags,
            "meta_description": meta_description,
            "url_slug": url_slug,
            "image_alt_text": image_alt_text,
            "current_step": "seo_metadata_complete"
        }

    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Failed to parse SEO metadata from LLM response: {e}")

        # Fallback generation
        slug = re.sub(r'[^a-z0-9\s-]', '', target_keyword.lower())
        slug = re.sub(r'[\s]+', '-', slug).strip('-')

        fallback_tags = [target_keyword] + secondary_keywords[:4]
        # Pad to 5 if needed
        while len(fallback_tags) < 5:
            fallback_tags.append(state.get("site_title", "blog"))

        return {
            "tags": fallback_tags[:5],
            "meta_description": f"Learn about {target_keyword}. {state.get('site_description', '')}"[:155],
            "url_slug": slug[:60],
            "image_alt_text": f"{target_keyword} - {state.get('selected_title', '')}"[:125],
            "current_step": "seo_metadata_complete_with_fallback",
            "error": str(e)
        }
