import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models import BaseChatModel

def get_llm() -> BaseChatModel:
    """
    Returns a configured LangChain chat model instance for Gemini.
    Raises ValueError if required environment variables are missing.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Missing required environment variable: GOOGLE_API_KEY")

    model_id = os.getenv("GITHUB_MCP_MODEL", "gemini-2.5-pro").strip()
    if not model_id:
        raise ValueError("Model ID cannot be empty.")

    return ChatGoogleGenerativeAI(
        model=model_id,
        api_key=api_key,
        streaming=True,
    )
