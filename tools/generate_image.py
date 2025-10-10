import os
import base64
import vertexai
from vertexai.preview.vision_models import ImageGenerationModel

async def generate_image(prompt: str) -> str:
    """
    Generate an image using Google's Imagen model via Vertex AI.
    """
    
    # Initialize Vertex AI
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    service_account_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    # Set credentials if service account path is provided
    if service_account_path and os.path.exists(service_account_path):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = service_account_path
    
    vertexai.init(project=project_id, location=location)
    
    # Load the Imagen model
    model = ImageGenerationModel.from_pretrained("imagegeneration@006")
    
    # Generate image
    images = model.generate_images(
        prompt=prompt,
        number_of_images=1,
        aspect_ratio="16:9",
        safety_filter_level="block_some",
        person_generation="allow_adult",
    )
    
    # Save image to a temporary location and return the path
    # Or upload to cloud storage and return URL
    image = images[0]
    output_file = f"generated_images/{hash(prompt)}.png"
    os.makedirs("generated_images", exist_ok=True)
    image.save(location=output_file)
    
    return output_file