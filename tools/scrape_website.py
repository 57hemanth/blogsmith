from typing import List, Dict
import aiohttp
from bs4 import BeautifulSoup

async def scrape_website(url: str) -> List[Dict[str, str]]:
    """
    Scrape blog articles from a website.
    You might want to use a more sophisticated tool like:
    - Firecrawl
    - Jina AI Reader
    - Scrapy
    """
    articles = []
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # This is a basic example - adjust selectors for actual sites
                article_elements = soup.find_all('article')[:5]
                
                for article in article_elements:
                    title_elem = article.find(['h1', 'h2', 'h3'])
                    link_elem = article.find('a')
                    
                    if title_elem and link_elem:
                        articles.append({
                            "title": title_elem.get_text(strip=True),
                            "url": link_elem.get('href', ''),
                            "content": article.get_text(strip=True)[:1000]  # First 1000 chars
                        })
    except Exception as e:
        print(f"Scraping error: {e}")
    
    return articles
