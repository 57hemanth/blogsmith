async def summarize_content(llm, content: str) -> str:
    """
    Summarize article content using LLM.
    """
    response = await llm.ainvoke([
        {"role": "system", "content": "Summarize this article in 2-3 sentences."},
        {"role": "user", "content": content}
    ])
    return response.content
