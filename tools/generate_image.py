import os
import aiohttp
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

IMAGE_PROVIDER = os.getenv("IMAGE_PROVIDER", "openai").lower()


async def _generate_image_google(prompt: str) -> bytes:
    """Generate an image using Google's Gemini 2.5 Flash Image model. Returns raw bytes."""
    from google import genai
    from google.genai import types

    api_key = os.getenv("GOOGLE_API_KEY")
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")

    if not api_key and not project_id:
        raise ValueError(
            "Either GOOGLE_API_KEY or GOOGLE_CLOUD_PROJECT environment variable is required for image generation."
        )

    logger.info("Initializing Google Gen AI client...")
    if api_key:
        client = genai.Client(api_key=api_key)

    logger.info("Generating image with Gemini 2.5 Flash Image...")
    config = types.GenerateContentConfig(
        response_modalities=["IMAGE"],
        image_config=types.ImageConfig(
            aspect_ratio="16:9",
        )
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[prompt],
        config=config
    )

    if not response or not hasattr(response, 'parts'):
        raise ValueError("No response received from the model")

    image_data = None
    for part in response.parts:
        if hasattr(part, 'inline_data') and part.inline_data:
            image_data = part.inline_data.data
            break

    if not image_data:
        raise ValueError("No image data found in the model response")

    return image_data


async def _generate_image_openai(prompt: str) -> bytes:
    """Generate an image using OpenAI gpt-image-1. Returns raw bytes."""
    import openai
    import base64

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required for OpenAI image generation.")

    logger.info("Generating image with OpenAI gpt-image-1...")
    client = openai.AsyncOpenAI(api_key=api_key)

    response = await client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1536x1024",
        quality="medium",
        n=1
    )

    image_data_obj = response.data[0]

    # gpt-image-1 returns base64 data; older models may return a URL
    if image_data_obj.b64_json:
        logger.info("Decoding base64 image data...")
        return base64.b64decode(image_data_obj.b64_json)
    elif image_data_obj.url:
        logger.info("Downloading generated image from URL...")
        async with aiohttp.ClientSession() as session:
            async with session.get(image_data_obj.url) as resp:
                if resp.status != 200:
                    raise ValueError(f"Failed to download image: HTTP {resp.status}")
                return await resp.read()
    else:
        raise ValueError("No image data or URL returned from OpenAI")


async def _save_image(image_data: bytes) -> str:
    """Save image bytes to disk and return the absolute path."""
    output_dir = "generated_images"
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"blog_image_{timestamp}.png")

    logger.info(f"Saving image to {output_file}...")
    with open(output_file, 'wb') as f:
        f.write(image_data)

    if os.path.exists(output_file):
        file_size = os.path.getsize(output_file)
        if file_size == 0:
            raise ValueError(f"Image file was created but is empty: {output_file}")
        logger.info(f"Image saved successfully! File: {output_file}, Size: {file_size:,} bytes")
        return os.path.abspath(output_file)
    else:
        raise FileNotFoundError(f"Image file was not created at {output_file}")


async def generate_image(prompt: str, return_bytes: bool = False):
    """
    Generate an image using the configured provider.

    Args:
        prompt: The image generation prompt
        return_bytes: If True, return raw image bytes. If False, save to file and return path.

    Set IMAGE_PROVIDER env var to 'openai' or 'google' (default: openai).
    """
    try:
        if IMAGE_PROVIDER == "openai":
            image_data = await _generate_image_openai(prompt)
        else:
            image_data = await _generate_image_google(prompt)

        if return_bytes:
            return image_data
        return await _save_image(image_data)
    except ValueError:
        raise
    except Exception as e:
        logger.error(f"Failed to generate/save image: {type(e).__name__}: {str(e)}")
        raise
