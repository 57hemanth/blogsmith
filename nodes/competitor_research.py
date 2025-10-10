from states import BlogState
from typing import Dict, Any
from config import llm
from tools import scrape_website, summarize_content

async def competitor_research_node(state: BlogState) -> Dict[str, Any]:
    """
    Research competitor blogs and summarize them.
    Uses web scraping + LLM summarization.
    """
    
    competitors_blogs = []
    
    for url in state.get("competitors_urls", []):
        try:
            # Scrape competitor website
            articles = await scrape_website(url)
            
            # Summarize top articles (limit to top 5)
            for article in articles[:5]:
                summary = await summarize_content(llm, article["content"])
                competitors_blogs.append({
                    "title": article["title"],
                    "url": article["url"],
                    "summary": summary,
                    "source": url
                })
        except Exception as e:
            print(f"Error scraping {url}: {e}")
    
    # Generate overall competitor summary
    if competitors_blogs:
        competitor_summary = await llm.ainvoke([
            {"role": "system", "content": "You are a content strategist."},
            {"role": "user", "content": f"""
            Analyze these competitor blog summaries and provide insights:
            {competitors_blogs}
            
            Focus on:
            - Common topics and themes
            - Content gaps we can exploit
            - Unique angles they're taking
            """}
        ])
    else:
        competitor_summary = "No competitor data available."
    
    return {
        "competitors_blogs": competitors_blogs,
        "competitor_summary": competitor_summary.content if hasattr(competitor_summary, 'content') else str(competitor_summary),
        "current_step": "competitor_research_complete"
    }

