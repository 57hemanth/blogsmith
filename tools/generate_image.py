import os
from google import genai
from google.genai import types
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

async def generate_image(prompt: str, return_bytes: bool = False) -> str | bytes:
    """
    Generate an image using Google's Gemini 2.5 Flash Image model.
    
    Args:
        prompt: The image generation prompt
        return_bytes: If True, return bytes instead of saving to file
    
    Required environment variables:
    - GOOGLE_API_KEY: Your Google API key (or GOOGLE_CLOUD_PROJECT for Vertex AI)
    - GOOGLE_CLOUD_PROJECT: Your GCP project ID (optional, for Vertex AI)
    
    Returns:
        Either the file path (str) if return_bytes=False, or image bytes (bytes) if return_bytes=True
    """
    try:
        # Get configuration from environment
        api_key = os.getenv("GOOGLE_API_KEY")
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        
        # Validate required configuration
        if not api_key and not project_id:
            raise ValueError(
                "Either GOOGLE_API_KEY or GOOGLE_CLOUD_PROJECT environment variable is required for image generation. "
                "Please set it in your .env file or skip image generation."
            )
        
        logger.info("Initializing Google Gen AI client...")
        
        # Initialize the client
        if api_key:
            client = genai.Client(api_key=api_key)
        
        # Load the Gemini 2.5 Flash Image model
        logger.info("Loading Gemini 2.5 Flash Image model...")
        
        # Generate image with proper parameters including aspect ratio
        logger.info("Generating image (this may take 20-30 seconds)...")
        
        # Configure generation with 16:9 aspect ratio
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
        
        # Get the image from the response
        if not response or not hasattr(response, 'parts'):
            raise ValueError("No response received from the model")
        
        # Extract image data from the response
        # Gemini returns image data in the response parts
        image_data = None
        for part in response.parts:
            if hasattr(part, 'inline_data') and part.inline_data:
                image_data = part.inline_data.data
                break
        
        if not image_data:
            raise ValueError("No image data found in the model response")
        
        logger.info("Image generated successfully")
        
        # Return bytes if requested (for R2 upload)
        if return_bytes:
            return image_data
        
        # Otherwise save to local file
        output_dir = "generated_images"
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f"blog_image_{timestamp}.png")
        
        logger.info(f"Saving image to {output_file}...")
        
        # Save the image bytes
        with open(output_file, 'wb') as f:
            f.write(image_data)
        
        # Verify file exists and has content
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            if file_size == 0:
                raise ValueError(f"Image file was created but is empty: {output_file}")
            
            logger.info(f"✅ Image saved successfully! File: {output_file}, Size: {file_size:,} bytes")
            
            # Return absolute path
            abs_path = os.path.abspath(output_file)
            return abs_path
        else:
            raise FileNotFoundError(f"Image file was not created at {output_file}")

    except ValueError as e:
        # Configuration errors
        logger.error(f"Configuration error: {str(e)}")
        raise
    except Exception as e:
        # Network or API errors
        logger.error(f"Failed to generate/save image: {type(e).__name__}: {str(e)}")
        logger.info("Tip: Check your GCP project settings, credentials, and API enablement")
        raise