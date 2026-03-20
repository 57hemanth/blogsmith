from typing import List, Dict, Optional
from langgraph.graph import MessagesState

class BlogState(MessagesState):
    # Input data
    site_url: str
    site_description: str
    site_title: str
    existing_blogs: List[Dict[str, str]]  # [{"title": "...", "url": "..."}, ...]
    competitors_urls: List[str]  # List of competitor URLs
    target_keyword: str  # Primary SEO keyword
    secondary_keywords: List[str]  # Secondary keywords

    # Research data
    competitors_blogs: List[Dict[str, str]]  # [{"title": "...", "summary": "...", "url": "..."}, ...]
    competitor_summary: str  # Overall summary of competitor content
    keywords: List[str]

    # Generation data
    titles: List[str]
    selected_title: str
    blog_outline: str
    blog_content: str
    featured_image_prompt: str
    featured_image: str  # URL or file path

    # SEO metadata
    tags: List[str]  # 5 SEO tags
    meta_description: str  # 140-155 character meta description
    image_alt_text: str  # Alt text with target keyword
    url_slug: str  # Clean hyphenated URL slug

    # Metadata
    current_step: str  # For tracking progress
    error: Optional[str]  # For error handling
