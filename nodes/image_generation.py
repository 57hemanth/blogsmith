from states import BlogState
from typing import Dict, Any
from config import llm
from tools import generate_image

async def image_generation_node(state: BlogState) -> Dict[str, Any]:
    """
    Generate a featured image for the blog.
    """
    
    # First, create an image prompt
    prompt_response = await llm.ainvoke([
        {"role": "system", "content": "You are an expert at creating image generation prompts."},
        {"role": "user", "content": f"""
        Create a DALL-E image prompt for a blog post titled: "{state["selected_title"]}"
        
        Blog content summary: {state["blog_content"][:500]}...
        
        Requirements:
        - Professional and eye-catching
        - Relevant to the topic
        - Modern, clean aesthetic
        - Suitable as a blog featured image
        
        Return ONLY the image prompt, no other text.
        """}
    ])
    
    image_prompt = prompt_response.content.strip()
    
    # Generate the image
    try:
        image_url = await generate_image(image_prompt)
    except Exception as e:
        print(f"Image generation failed: {e}")
        image_url = ""
    
    return {
        "featured_image_prompt": image_prompt,
        "featured_image": image_url,
        "current_step": "image_generation_complete"
    }
