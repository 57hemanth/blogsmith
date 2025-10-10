import asyncio
from graphs import run_blog_writer

async def main():
    result = await run_blog_writer(
        site_url="https://martsonline.com",
        site_title="Dmart Near Me",
        site_description="A blog about Dmarts in your area.",
        existing_blogs=[
            {"title": "Best deals on dmart products", "url": "https://martsonline.com/best-deals-on-dmart-products"},
            {"title": "Save more on your groceries from dmart shopping", "url": "https://martsonline.com/save-more-on-your-groceries-from-dmart-shopping"},
        ],
        competitors_urls=[
            "https://dmartnearme.com/"
        ]
    )
    
    print("=" * 50)
    print(f"Selected Title: {result['selected_title']}")
    print("=" * 50)
    print(f"Blog Content:\n{result['blog_content']}")
    print("=" * 50)
    print(f"Featured Image: {result['featured_image']}")
    
    # Save to file
    with open("generated_blog.md", "w") as f:
        f.write(f"# {result['selected_title']}\n\n")
        f.write(f"![Featured Image]({result['featured_image']})\n\n")
        f.write(result['blog_content'])

if __name__ == "__main__":
    asyncio.run(main())