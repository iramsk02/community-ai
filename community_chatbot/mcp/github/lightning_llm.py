import os
from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel


def get_llm() -> BaseChatModel:
    api_key = os.getenv("LIGHTNING_API_KEY")
    if not api_key:
        raise ValueError(
            "Missing required environment variable: LIGHTNING_API_KEY"
        )

    base_url = os.getenv("LIGHTNING_BASE_URL")
    if not base_url:
        raise ValueError(
            "Missing required environment variable: LIGHTNING_BASE_URL"
        )

    # Model name from your Lightning AI deployment
    # Can be overridden via environment variable
    model_id = os.getenv(
        "MODEL", "meta-llama/Llama-3.3-70B-Instruct"
    ).strip()
    if not model_id:
        raise ValueError("Model ID cannot be empty.")

    # Optional: timeout and max_retries for robustness
    timeout = int(os.getenv("LIGHTNING_TIMEOUT", "60"))
    max_retries = int(os.getenv("LIGHTNING_MAX_RETRIES", "3"))

    return ChatOpenAI(
        api_key=api_key,
        base_url=base_url,
        model=model_id,
        temperature=0.7,
        streaming=True,
        timeout=timeout,
        max_retries=max_retries,
    )
