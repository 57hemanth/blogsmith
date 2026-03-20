from states import BlogState
from typing import Dict, Any
from config import llm
from tools import generate_image
from tools.gcs_upload import upload_image_to_gcs
import logging
import os

logger = logging.getLogger(__name__)

# Enough context for the prompt-writer LLM without flooding the image model later.
_OUTLINE_SNIPPET_LEN = 2000
_CONTENT_SNIPPET_LEN = 2500

# Appended so the image reads as a blog hero with title + topic assets, not a generic stock shot.
_PROMPT_STYLE_SUFFIX = (
    "Visual style lock: blog featured image (article hero / Open Graph), 16:9 landscape. "
    "Modern flat editorial illustration: bold solid color fields, simple geometric shapes, chunky icons and props, "
    "crisp edges, minimal or no gradients, no photorealism, no cinematic lighting, no generic stock-photo people. "
    "Include one short on-image headline (the exact short phrase specified in the prompt—not the full blog title). "
    "Optional: a tiny second line of at most a few words; never paste the full meta description. "
    "Include multiple concrete visual elements (objects, symbols, small pictograms) tied to the article—not empty abstract shapes only. "
    "Balanced composition, readable at thumbnail size. Use a deliberate 4–5 color palette (name colors or hex). "
    "No watermarks, no real third-party logos, no celebrity likenesses."
)


async def image_generation_node(state: BlogState) -> Dict[str, Any]:
    """
    Generate a featured image for the blog; upload to GCS when configured, else save locally.
    """
    logger.info("Starting featured image generation...")

    try:
        # First, create an image prompt
        logger.info("   Creating image prompt...")
        selected_title = (state.get("selected_title") or "").strip()
        if not selected_title:
            raise ValueError("selected_title is required for featured image generation")

        alt_text = (state.get("image_alt_text") or "").strip()
        site_description = (state.get("site_description") or "").strip()
        meta_description = (state.get("meta_description") or "").strip()
        outline = (state.get("blog_outline") or "").strip()
        content = (state.get("blog_content") or "").strip()
        target_kw = (state.get("target_keyword") or "").strip()
        secondary = state.get("secondary_keywords") or []
        if isinstance(secondary, str):
            secondary = [secondary]
        secondary_str = ", ".join(s for s in secondary if s) if secondary else ""
        tags = state.get("tags") or []
        if isinstance(tags, str):
            tags = [tags]
        tags_str = ", ".join(t for t in tags if t) if tags else ""
        keywords = state.get("keywords") or []
        if isinstance(keywords, list):
            kw_preview = ", ".join(str(k) for k in keywords[:12])
        else:
            kw_preview = str(keywords)

        outline_snip = outline[:_OUTLINE_SNIPPET_LEN] + ("…" if len(outline) > _OUTLINE_SNIPPET_LEN else "")
        content_snip = content[:_CONTENT_SNIPPET_LEN] + ("…" if len(content) > _CONTENT_SNIPPET_LEN else "")

        system = """You write prompts for text-to-image models (DALL-E, Gemini Image, etc.).

Goal: one blog featured image (article hero / social preview): flat modern editorial illustration with a SHORT on-image headline (one line) plus topic-specific visual assets—not photorealistic stock, not a wall of text.

On-image copy rules (critical):
- Do NOT put the full long blog title on the graphic. Invent ONE punchy headline for the artwork: maximum 8 words, ideally 3–6, Title Case or ALL CAPS as you prefer—must distill the real title’s meaning (the full title is context only).
- If the real blog title is already 8 words or fewer, you may use it verbatim as the on-image line; otherwise you must shorten.
- Do NOT paste the meta description or any long sentence on the image. Optional micro sub-line only: maximum 5 words, only if it adds hook; otherwise omit entirely.
- In your output prompt, state the exact short headline string the image generator must render (so spelling is fixed).

Required content in every prompt you write:
1) Headline typography: describe placement and style (bold clean sans-serif, color block behind text, etc.) and include the exact short headline string to paint—never the full article title when it exceeds 8 words.
2) Related assets: at least 4–6 distinct visual elements from the outline, excerpt, keywords, and tags—concrete objects, symbols, or chunky icons. Name each in the prompt.
3) Palette and layout: cohesive 4–5 colors (names or hex), 16:9, balanced, readable at thumbnail size.

Avoid: watermarks, invented brand logos, real trademarked marks, celebrity likenesses, cinematic photo look, empty backgrounds with no props.

Output one continuous English prompt (no markdown, no section labels). About 220–360 words: exact short headline, then assets, colors, composition, style."""

        user_parts = [
            "## Full blog title (context only—compress to a one-liner for the image, do not put this whole string on the art unless it is already short)",
            selected_title,
            "",
            "## Meta description (context only—do not put this full text on the image; at most inspire a 5-word micro line or omit)",
            meta_description or "N/A",
            "",
            "## Tone / niche context",
            f"Description: {site_description or 'N/A'}",
            "",
        ]

        user_parts.extend(
            [
            "## SEO / topic signals (turn into concrete icons/props/symbols)",
            f"Primary keyword: {target_kw or 'N/A'}",
            f"Secondary keywords: {secondary_str or 'N/A'}",
            f"Keyword list (sample): {kw_preview or 'N/A'}",
            f"Tags: {tags_str or 'N/A'}",
            "",
            "## Outline — mine section themes for specific objects and scenes to draw",
            outline_snip or "N/A",
            "",
            "## Article excerpt — mine nouns and scenarios for specific illustrated assets",
            content_snip or "N/A",
            "",
            ]
        )
        if alt_text:
            user_parts.extend(
                [
                    "## Image alt intent (reinforce subject matter; may inform small symbols)",
                    alt_text,
                    "",
                ]
            )
        user_parts.append(
            "Write the final image-generation prompt now. Requirements: (1) one short on-image headline (exact string in the prompt; "
            "not the full title unless it is already ≤8 words), (2) optional ≤5-word sub-line or none—never full meta description, "
            "(3) at least 4–6 named visual assets, (4) flat illustration style and explicit colors."
        )
        user_message = "\n".join(user_parts)

        prompt_response = await llm.ainvoke(
            [
                {"role": "system", "content": system},
                {"role": "user", "content": user_message},
            ]
        )

        image_prompt = f"{prompt_response.content.strip()}\n\n{_PROMPT_STYLE_SUFFIX}".strip()
        logger.info(f"   Prompt: {image_prompt[:100]}...")

        # Generate the image
        logger.info("   Generating image with AI...")
        try:
            # Get image data as bytes
            image_data = await generate_image(image_prompt, return_bytes=True)
            
            # Check if running in production with GCS configured
            if os.getenv('GCS_BUCKET_NAME'):
                logger.info("   Uploading to Google Cloud Storage...")
                image_url = await upload_image_to_gcs(image_data)
            else:
                # Fallback to local storage for development
                logger.warning("   GCS not configured, saving locally...")
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_dir = "generated_images"
                os.makedirs(output_dir, exist_ok=True)
                output_file = os.path.join(output_dir, f"blog_image_{timestamp}.png")
                
                with open(output_file, 'wb') as f:
                    f.write(image_data)
                
                image_url = os.path.abspath(output_file)
            
            logger.info(f"✅ Image generated and stored: {image_url}")
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            image_url = ""

        return {
            "featured_image_prompt": image_prompt,
            "featured_image": image_url,
            "current_step": "image_generation_complete"
        }

    except Exception as e:
        logger.error(f"Image generation node failed: {e}")
        return {
            "featured_image_prompt": "",
            "featured_image": "",
            "current_step": "image_generation_failed",
            "error": str(e)
        }