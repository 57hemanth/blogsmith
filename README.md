# AI Blog Writer Agent 🤖✍️

An intelligent blog writing agent built with LangGraph and LangChain that automates the entire blog creation process from research to publication.

## Features

- 🔍 **Competitor Research**: Automatically scrape and analyze competitor blogs
- 🔑 **Keyword Research**: Generate SEO-optimized keywords based on your site and competitors
- 📝 **Title Generation**: Create multiple compelling blog title options
- 🎯 **Smart Selection**: AI-powered title selection based on SEO and engagement potential
- 📋 **Outline Generation**: Structured content outlines for better organization
- ✍️ **Content Writing**: Generate high-quality, SEO-optimized blog posts (1500-2500 words)
- 🖼️ **Image Generation**: Create featured images using AI (DALL-E)

## Architecture

Built with **LangGraph** for orchestrating a multi-step agent workflow:

```
START → Competitor Research → Keyword Research → Title Generation 
→ Title Selection → Outline Generation → Content Generation 
→ Image Generation → END
```

### Key Components

- **State Management**: TypedDict-based state tracking across all nodes
- **Conditional Routing**: Smart workflow decisions (skip competitor research if no URLs provided)
- **Checkpointing**: SQLite-based persistence for pause/resume capability
- **Error Handling**: Robust error recovery and logging
- **Visual Debugging**: Full LangGraph Studio integration

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd blog-writing-agent

# Run setup script
chmod +x setup.sh
./setup.sh

# Or manual setup
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file:

```env
# Google AI (Gemini)
GOOGLE_API_KEY=your_google_api_key_here

# Or OpenAI
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Run with LangGraph Studio (Recommended)

```bash
# Install LangGraph CLI
pip install langgraph-cli

# Start the studio
langgraph dev
```

Open your browser at `http://localhost:8123` and start creating blogs!

See [LANGGRAPH_STUDIO.md](./LANGGRAPH_STUDIO.md) for detailed Studio usage.

### 4. Or Run Programmatically

```bash
python main.py
```

### 5. Run with Docker

The API server runs as a container on port 8080. Ensure you have a `.env` file in the project root (see Configuration).

```bash
# Build the image
docker build -t blogsmith .

# Run the container (pass env from .env)
docker run --rm -p 8080:8080 --env-file .env blogsmith
```

- **API:** `http://localhost:8080`
- **Docs:** `http://localhost:8080/docs`
- **Run in background:** add `-d` to `docker run`
- **Custom env vars:** use `-e KEY=value` or keep using `--env-file .env`

For GCS image uploads, set `GCS_BUCKET_NAME` and `GOOGLE_APPLICATION_CREDENTIALS` in `.env` (or mount the credentials file and set the path inside the container).

## Project Structure

```
blog-writing-agent/
├── graphs/
│   ├── __init__.py
│   └── blog_writer.py       # Main workflow graph
├── nodes/
│   ├── __init__.py
│   ├── competitor_research.py
│   ├── keyword_research.py
│   ├── title_generation.py
│   ├── title_selection.py
│   ├── outline_generation.py
│   ├── content_generation.py
│   └── image_generation.py
├── states/
│   ├── __init__.py
│   └── BlogState.py         # State schema
├── tools/
│   └── ...                  # Utility functions
├── config/
│   └── ...                  # LLM configuration
├── langgraph.json           # Studio configuration
├── requirements.txt
├── main.py                  # CLI entry point
└── README.md
```

## Usage Example

### Via Studio

1. Open LangGraph Studio
2. Load the project
3. Use this input:

```json
{
  "site_url": "https://yoursite.com",
  "site_title": "Your Blog Title",
  "site_description": "A blog about...",
  "existing_blogs": [
    {"title": "Previous Blog 1", "url": "https://..."}
  ],
  "competitors_urls": [
    "https://competitor1.com",
    "https://competitor2.com"
  ],
  "messages": []
}
```

### Via Python

```python
import asyncio
from graphs.blog_writer import graph

async def generate_blog():
    config = {"configurable": {"thread_id": "test_run"}}
    
    initial_state = {
        "site_url": "https://yoursite.com",
        "site_title": "Your Blog",
        "site_description": "A blog about tech",
        "existing_blogs": [],
        "competitors_urls": ["https://competitor.com"],
        "messages": []
    }
    
    result = await graph.ainvoke(initial_state, config)
    print(result['blog_content'])

asyncio.run(generate_blog())
```

## State Schema

The agent maintains this state across all nodes:

```python
class BlogState(MessagesState):
    # Input
    site_url: str
    site_title: str
    site_description: str
    existing_blogs: List[Dict[str, str]]
    competitors_urls: List[str]
    
    # Research
    competitors_blogs: List[Dict[str, str]]
    competitor_summary: str
    keywords: List[str]
    
    # Generation
    titles: List[str]
    selected_title: str
    blog_outline: str
    blog_content: str
    featured_image_prompt: str
    featured_image: str
    
    # Metadata
    current_step: str
    error: Optional[str]
```

## Workflow Nodes

### 1. Competitor Research
- Scrapes competitor websites
- Extracts blog articles
- Generates summaries and insights

### 2. Keyword Research
- Analyzes site description
- Incorporates competitor insights
- Generates 15-20 SEO keywords

### 3. Title Generation
- Creates 10 title options
- Ensures no duplicates with existing blogs
- Various formats (how-to, listicles, guides)

### 4. Title Selection
- AI-powered selection
- Based on SEO potential and engagement

### 5. Outline Generation
- Structured blog outline
- 4-6 main sections
- Word count suggestions

### 6. Content Generation
- 1500-2500 word blog posts
- SEO-optimized
- Markdown formatted
- Engaging and valuable

### 7. Image Generation
- Creates featured images
- DALL-E integration
- Professional and relevant

## Advanced Features

### Conditional Routing
Automatically skips competitor research if no competitors are provided.

### Checkpointing
All progress is saved to `checkpoints.db`. You can pause and resume runs.

### Error Recovery
Robust error handling with detailed logging at each step.

### Real-time Monitoring
With LangGraph Studio, watch each node execute in real-time.

## Debugging with Studio

LangGraph Studio provides:

- 📊 **Visual Graph**: See your workflow structure
- ▶️ **Step-by-Step Execution**: Run one node at a time
- 🔍 **State Inspector**: View state changes at each step
- 📝 **Logs**: Detailed execution logs
- ⏸️ **Pause/Resume**: Checkpoint-based persistence
- 🐛 **Error Debugging**: See exactly where and why failures occur

## Configuration

### LangGraph Studio Config (`langgraph.json`)

```json
{
  "dependencies": ["."],
  "graphs": {
    "blog_writer": "./graphs/blog_writer.py:graph"
  },
  "env": ".env"
}
```

### Environment Variables

Used by both local runs and Docker. Copy `.env.example` to `.env` and fill in values.

```env
# LLM & image providers
LLM_PROVIDER=openai
IMAGE_PROVIDER=openai
OPENAI_API_KEY=your_key_here
# GOOGLE_API_KEY=your_key_here
# GOOGLE_CLOUD_PROJECT=your_gcp_project_id

# Optional: GCS image upload (Docker/production)
# GCS_BUCKET_NAME=your-bucket-name
# GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

LOG_LEVEL=INFO
```

## Requirements

- Python 3.9+
- LangGraph
- LangChain
- Google AI or OpenAI API key

## Troubleshooting

### Graph won't load in Studio
- Check `langgraph.json` is in project root
- Verify all imports in `graphs/blog_writer.py`
- Ensure dependencies are installed

### API Errors
- Verify `.env` file has correct API keys
- Check API key permissions
- Review rate limits

### Node Failures
- Check logs in Studio console
- Inspect state before failed node
- Verify input data format

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests if applicable
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangGraph Studio](https://langchain-ai.github.io/langgraph/studio/)
- [LangChain Docs](https://python.langchain.com/)

## Support

For issues or questions:
- Open a GitHub issue
- Check [LANGGRAPH_STUDIO.md](./LANGGRAPH_STUDIO.md) for Studio-specific help

---

Built with ❤️ using LangGraph and LangChain

