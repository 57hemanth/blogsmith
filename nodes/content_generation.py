from states import BlogState
from typing import Dict, Any
from config import llm

async def content_generation_node(state: BlogState) -> Dict[str, Any]:
    """
    Generate the full blog content.
    """
    
    prompt = f"""
    Write a comprehensive, high-quality blog post.
    
    Title: {state["selected_title"]}
    
    Outline:
    {state["blog_outline"]}
    
    Context:
    - Website: {state["site_title"]} - {state["site_description"]}
    - Target Keywords: {", ".join(state["keywords"])}
    - Competitor Insights: {state.get("competitor_summary", "")}
    
    Requirements:
    - 1500-2500 words
    - SEO-optimized (naturally include keywords)
    - Engaging and valuable to readers
    - Use markdown formatting
    - Include clear headers (H2, H3)
    - Add bullet points and numbered lists where appropriate
    - Conversational yet professional tone
    - Include a strong introduction and conclusion
    
    Write the complete blog post now.
    """
    
    response = await llm.ainvoke([
        {"role": "system", "content": "You are an expert content writer specializing in engaging, SEO-optimized blog posts."},
        {"role": "user", "content": prompt}
    ])
    
    return {
        "blog_content": response.content,
        "current_step": "content_generation_complete"
    }
