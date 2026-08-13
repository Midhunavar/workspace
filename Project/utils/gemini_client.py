"""
Gemini LLM factory for the AI review node (preloaded).

Returns a ready-to-use ChatGoogleGenerativeAI — the standard LangChain chat model
for Gemini, built on the current google-genai SDK. The model name and API key
always come from the .env file, so associates choose their own model.
"""

from langchain_google_genai import ChatGoogleGenerativeAI

from config import config


def get_review_llm(temperature: float = 0.2) -> ChatGoogleGenerativeAI:
    """Return a Gemini chat model using the model and key from the .env file."""
    return ChatGoogleGenerativeAI(
        model=config.gemini_model,
        google_api_key=config.gemini_api_key,
        temperature=temperature,
    )
