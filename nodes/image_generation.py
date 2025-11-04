from states import BlogState
from typing import Dict, Any
from config import llm
from tools import generate_image
from tools.gcs_upload import upload_image_to_gcs
import logging
import os

logger = logging.getLogger(__name__)

async def image_generation_node(state: BlogState) -> Dict[str, Any]:
    """
    Generate a featured image for the blog and upload to R2.
    """
    logger.info("🖼️  Starting featured image generation...")
    
    try:
        # First, create an image prompt
        logger.info("   Creating image prompt...")
        prompt_response = await llm.ainvoke([
            {"role": "system", "content": "You are an expert at creating image generation prompts."},
            {"role": "user", "content": f"""
            Create a DALL-E image prompt for a blog post titled: "{state["selected_title"]}"
            
            Blog content summary: {state.get("blog_content", "")[:500]}...
            
            Requirements:
            - Professional and eye-catching
            - Relevant to the topic
            - Modern, clean aesthetic
            - Suitable as a blog featured image
            
            Return ONLY the image prompt, no other text.
            """}
        ])
        
        image_prompt = prompt_response.content.strip()
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
            logger.error(f"❌ Image generation failed: {e}")
            image_url = ""
        
        return {
            "featured_image_prompt": image_prompt,
            "featured_image": image_url,
            "current_step": "image_generation_complete"
        }
        
    except Exception as e:
        logger.error(f"❌ Image generation node failed: {e}")
        return {
            "featured_image_prompt": "",
            "featured_image": "",
            "current_step": "image_generation_failed",
            "error": str(e)
        }