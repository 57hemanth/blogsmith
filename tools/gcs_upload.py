import os
from google.cloud import storage
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

def create_gcs_client():
    """Create Google Cloud Storage client"""
    # GCS client automatically uses:
    # 1. GOOGLE_APPLICATION_CREDENTIALS env var (path to service account JSON)
    # 2. Application Default Credentials if running on GCP
    # 3. gcloud auth application-default login credentials
    
    try:
        return storage.Client()
    except Exception as e:
        raise ValueError(
            f"Failed to create GCS client: {e}. "
            "Please ensure GOOGLE_APPLICATION_CREDENTIALS is set to your service account JSON file, "
            "or you're running on GCP with proper IAM permissions, "
            "or run 'gcloud auth application-default login'."
        )

async def upload_image_to_gcs(
    image_data: bytes,
    bucket_name: str = None,
    filename: str = None
) -> str:
    """
    Upload an image to Google Cloud Storage.
    
    Args:
        image_data: The image bytes to upload
        bucket_name: GCS bucket name (defaults to GCS_BUCKET_NAME env var)
        filename: Optional custom filename
    
    Returns:
        Public URL of the uploaded image
    
    Required Environment Variables:
        - GCS_BUCKET_NAME: Your GCS bucket name
        - GOOGLE_APPLICATION_CREDENTIALS: Path to service account JSON (optional if using other auth methods)
    """
    try:
        client = create_gcs_client()
        
        # Get bucket name from env if not provided
        if bucket_name is None:
            bucket_name = os.getenv('GCS_BUCKET_NAME')
            if not bucket_name:
                raise ValueError("GCS_BUCKET_NAME environment variable is required")
        
        # Get the bucket
        bucket = client.bucket(bucket_name)
        
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            filename = f"blog_images/{timestamp}_{unique_id}.png"
        
        logger.info(f"📤 Uploading image to GCS: gs://{bucket_name}/{filename}")
        
        # Create blob and upload
        blob = bucket.blob(filename)
        blob.upload_from_string(
            image_data,
            content_type='image/png'
        )
        
        # Make the blob publicly accessible
        blob.make_public()
        
        # Generate public URL
        public_url = blob.public_url
        
        logger.info(f"✅ Image uploaded successfully: {public_url}")
        return public_url
        
    except Exception as e:
        logger.error(f"❌ Failed to upload image to GCS: {e}")
        raise

def setup_gcs_bucket_cors(bucket_name: str = None):
    """
    Set up CORS policy for GCS bucket to allow web access to images.
    This is a utility function you can run once to configure your bucket.
    """
    try:
        client = create_gcs_client()
        
        if bucket_name is None:
            bucket_name = os.getenv('GCS_BUCKET_NAME')
            if not bucket_name:
                raise ValueError("GCS_BUCKET_NAME environment variable is required")
        
        bucket = client.bucket(bucket_name)
        
        # Set CORS policy
        bucket.cors = [
            {
                "origin": ["*"],
                "method": ["GET"],
                "responseHeader": ["Content-Type"],
                "maxAgeSeconds": 3600
            }
        ]
        bucket.patch()
        
        logger.info(f"✅ CORS policy set for bucket: {bucket_name}")
        
    except Exception as e:
        logger.error(f"❌ Failed to set CORS policy: {e}")
        raise
