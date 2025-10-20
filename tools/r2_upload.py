import boto3
from botocore.config import Config
from datetime import datetime
import uuid
import os
import logging

logger = logging.getLogger(__name__)

def create_r2_client():
    """Create S3-compatible R2 client"""
    account_id = os.getenv('CLOUDFLARE_ACCOUNT_ID')
    access_key = os.getenv('R2_ACCESS_KEY_ID')
    secret_key = os.getenv('R2_SECRET_ACCESS_KEY')
    
    if not all([account_id, access_key, secret_key]):
        raise ValueError("Missing R2 credentials in environment variables")
    
    return boto3.client(
        's3',
        endpoint_url=f'https://{account_id}.r2.cloudflarestorage.com',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=Config(signature_version='s3v4'),
        region_name='auto'
    )

async def upload_image_to_r2(
    image_data: bytes,
    bucket_name: str = None,
    filename: str = None
) -> str:
    """
    Upload an image to Cloudflare R2 storage.
    
    Args:
        image_data: The image bytes to upload
        bucket_name: R2 bucket name
        filename: Optional custom filename
    
    Returns:
        Public URL of the uploaded image
    """
    try:
        s3_client = create_r2_client()
        
        # Get bucket name from env if not provided
        if bucket_name is None:
            bucket_name = os.getenv('R2_BUCKET_NAME', 'blog-agent')
        
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            filename = f"blog_images/{timestamp}_{unique_id}.png"
        
        logger.info(f"📤 Uploading image to R2: {filename}")
        
        # Upload to R2
        s3_client.put_object(
            Bucket=bucket_name,
            Key=filename,
            Body=image_data,
            ContentType='image/png',
            CacheControl='public, max-age=31536000'
        )
        
        # Generate public URL
        # Option 1: Use R2_ENDPOINT from wrangler config
        r2_endpoint = os.getenv('R2_ENDPOINT')
        if r2_endpoint:
            public_url = f"{r2_endpoint}/{filename}"
        else:
            # Option 2: Use custom domain configured for R2 bucket
            public_domain = os.getenv('R2_PUBLIC_DOMAIN')
            if public_domain:
                public_url = f"https://{public_domain}/{filename}"
            else:
                # Fallback: Use bucket name in URL
                public_url = f"https://pub-{bucket_name}.r2.dev/{filename}"
        
        logger.info(f"✅ Image uploaded successfully: {public_url}")
        return public_url
        
    except Exception as e:
        logger.error(f"❌ Failed to upload image to R2: {e}")
        raise