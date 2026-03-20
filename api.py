from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging
from graphs.blog_writer import graph
from datetime import datetime
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Blog Writing Agent API")

class BlogRequest(BaseModel):
    site_url: str
    site_title: str
    site_description: str
    existing_blogs: List[Dict[str, str]] = []
    competitors_urls: List[str] = []
    target_keyword: str = ""
    secondary_keywords: List[str] = []
    thread_id: Optional[str] = None

class BlogResponse(BaseModel):
    success: bool
    title: Optional[str] = None
    content: Optional[str] = None
    featured_image: Optional[str] = None
    keywords: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    meta_description: Optional[str] = None
    url_slug: Optional[str] = None
    image_alt_text: Optional[str] = None
    error: Optional[str] = None

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/generate-blog", response_model=BlogResponse)
async def generate_blog(request: BlogRequest):
    """
    Generate a blog post with AI
    """
    try:
        logger.info(f"Starting blog generation for: {request.site_title}")

        # Prepare initial state
        initial_state = {
            "site_url": request.site_url,
            "site_title": request.site_title,
            "site_description": request.site_description,
            "existing_blogs": request.existing_blogs,
            "competitors_urls": request.competitors_urls,
            "target_keyword": request.target_keyword,
            "secondary_keywords": request.secondary_keywords,
            "messages": []
        }

        # Run the graph
        result = await graph.ainvoke(initial_state)

        logger.info(f"Blog generation complete: {result.get('selected_title')}")

        return BlogResponse(
            success=True,
            title=result.get("selected_title"),
            content=result.get("blog_content"),
            featured_image=result.get("featured_image"),
            keywords=result.get("keywords", []),
            tags=result.get("tags", []),
            meta_description=result.get("meta_description"),
            url_slug=result.get("url_slug"),
            image_alt_text=result.get("image_alt_text"),
        )

    except Exception as e:
        logger.error(f"Error generating blog: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "name": "Blog Writing Agent API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "generate_blog": "/generate-blog (POST)"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
