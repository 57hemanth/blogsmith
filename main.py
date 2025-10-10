import asyncio
import logging
from graphs.blog_writer import graph
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """
    Run the blog writer agent programmatically.
    For visual debugging, use LangGraph Studio instead (see LANGGRAPH_STUDIO.md)
    """
    logger.info("🚀 Starting Blog Writer Agent")
    
    # Configuration for the run
    config = {
        "configurable": {
            "thread_id": f"blog_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }
    }
    
    # Initial state
    initial_state = {
        "site_url": "https://martsonline.com",
        "site_title": "Dmart Near Me",
        "site_description": "A blog about Dmarts in your area.",
        "existing_blogs": [
            {"title": "Best deals on dmart products", "url": "https://martsonline.com/best-deals-on-dmart-products"},
            {"title": "Save more on your groceries from dmart shopping", "url": "https://martsonline.com/save-more-on-your-groceries-from-dmart-shopping"},
        ],
        "competitors_urls": [
            "https://dmartnearme.com/"
        ],
        "messages": []
    }
    
    try:
        # Stream events for real-time monitoring
        result = None
        async for event in graph.astream(initial_state, config, stream_mode="values"):
            result = event
            current_step = event.get("current_step", "unknown")
            
            # Log progress
            if current_step and current_step != "unknown":
                logger.info(f"✅ Completed: {current_step}")
            
            # Show keywords when available
            if "keywords" in event and event["keywords"]:
                logger.info(f"🔑 Keywords generated: {', '.join(event['keywords'][:5])}...")
            
            # Show title when selected
            if "selected_title" in event and event["selected_title"]:
                logger.info(f"📝 Title selected: {event['selected_title']}")
        
        # Final results
        logger.info("=" * 70)
        logger.info("✨ BLOG GENERATION COMPLETE")
        logger.info("=" * 70)
        logger.info(f"📌 Title: {result.get('selected_title', 'N/A')}")
        logger.info(f"📊 Content Length: {len(result.get('blog_content', ''))} characters")
        logger.info(f"🖼️  Featured Image: {result.get('featured_image', 'N/A')}")
        
        # Save to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"generated_blog_{timestamp}.md"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# {result.get('selected_title', 'Untitled')}\n\n")
            if result.get('featured_image'):
                f.write(f"![Featured Image]({result['featured_image']})\n\n")
            if result.get('keywords'):
                f.write(f"**Keywords:** {', '.join(result['keywords'][:10])}\n\n")
            f.write("---\n\n")
            f.write(result.get('blog_content', ''))
        
        logger.info(f"💾 Blog saved to: {filename}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Error in workflow: {e}", exc_info=True)
        return None


if __name__ == "__main__":
    asyncio.run(main())