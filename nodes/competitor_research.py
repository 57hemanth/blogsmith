from states import BlogState
from typing import Dict, Any
from config import llm
from tools import scrape_website, summarize_content
import logging

logger = logging.getLogger(__name__)

async def competitor_research_node(state: BlogState) -> Dict[str, Any]:
    """
    Research competitor blogs and summarize them.
    Uses web scraping + LLM summarization.
    """
    logger.info("🔍 Starting competitor research...")
    competitors_urls = state.get("competitors_urls", [])
    logger.info(f"📋 Found {len(competitors_urls)} competitor URLs to analyze")
    
    competitors_blogs = []
    failed_urls = []
    
    for idx, url in enumerate(competitors_urls, 1):
        try:
            logger.info(f"🌐 [{idx}/{len(competitors_urls)}] Scraping {url}...")
            # Scrape competitor website
            articles = await scrape_website(url)
            logger.info(f"✅ Found {len(articles)} articles from {url}")
            
            # Summarize top articles (limit to top 5)
            for article_idx, article in enumerate(articles[:5], 1):
                try:
                    logger.debug(f"📝 Summarizing article {article_idx}/5: {article['title'][:50]}...")
                    summary = await summarize_content(llm, article["content"])
                    competitors_blogs.append({
                        "title": article["title"],
                        "url": article["url"],
                        "summary": summary,
                        "source": url
                    })
                except Exception as e:
                    logger.warning(f"⚠️  Failed to summarize article: {str(e)}")
                    
        except Exception as e:
            logger.error(f"❌ Error scraping {url}: {str(e)}")
            failed_urls.append(url)
    
    logger.info(f"📊 Successfully analyzed {len(competitors_blogs)} articles from competitors")
    
    # Generate overall competitor summary
    if competitors_blogs:
        logger.info("🧠 Generating strategic insights from competitor analysis...")
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
        logger.info("✅ Competitor insights generated successfully")
    else:
        logger.warning("⚠️  No competitor data available - proceeding without competitive insights")
        competitor_summary = "No competitor data available."
    
    result = {
        "competitors_blogs": competitors_blogs,
        "competitor_summary": competitor_summary.content if hasattr(competitor_summary, 'content') else str(competitor_summary),
        "current_step": "competitor_research_complete"
    }
    
    if failed_urls:
        result["error"] = f"Failed to scrape: {', '.join(failed_urls)}"
        logger.warning(f"⚠️  Some URLs failed: {', '.join(failed_urls)}")
    
    return result

