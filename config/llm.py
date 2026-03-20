import os
from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()

if LLM_PROVIDER == "openai":
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(
        model="gpt-4.1",
        temperature=0.3,
        max_tokens=32768,
        api_key=os.getenv("OPENAI_API_KEY")
    )
else:
    from langchain_google_genai import ChatGoogleGenerativeAI
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",
        temperature=0.7,
        api_key=os.getenv("GOOGLE_API_KEY")
    )
