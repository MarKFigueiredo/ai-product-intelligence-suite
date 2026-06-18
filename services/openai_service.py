"""OpenAI access, JSON parsing, and safe generation helpers."""
from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

load_dotenv()


def get_api_key() -> str:
    """Read API key from local .env or Streamlit secrets."""
    env_key = os.getenv("OPENAI_API_KEY", "").strip()
    if env_key:
        return env_key
    try:
        return str(st.secrets.get("OPENAI_API_KEY", "")).strip()
    except Exception:
        return ""


def get_client() -> OpenAI:
    api_key = get_api_key()
    if not api_key:
        raise ValueError("OPENAI_API_KEY is missing. Enable Demo Mode or add a valid API key.")
    return OpenAI(api_key=api_key)


def extract_json(text: str) -> Dict[str, Any]:
    """Best-effort extraction of a JSON object from model text."""
    if not text:
        return {}
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fenced:
        try:
            return json.loads(fenced.group(1))
        except json.JSONDecodeError:
            pass

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = text[start : end + 1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            return {"raw_markdown": text}
    return {"raw_markdown": text}


def call_model_json(prompt: str, model: str, max_output_tokens: int, demo_data: Optional[Dict[str, Any]] = None, demo_mode: bool = True) -> Dict[str, Any]:
    """Generate a JSON object or return deterministic demo data."""
    if demo_mode:
        return demo_data or {"title": "Demo output", "summary": "Enable API mode to generate a real response."}

    client = get_client()
    try:
        response = client.responses.create(
            model=model,
            input=prompt,
            max_output_tokens=max_output_tokens,
        )
        return extract_json(getattr(response, "output_text", ""))
    except OpenAIError:
        raise


def call_model_text(prompt: str, model: str, max_output_tokens: int, demo_text: str = "", demo_mode: bool = True) -> str:
    if demo_mode:
        return demo_text or "Demo Mode is enabled. Disable Demo Mode to call the API."
    client = get_client()
    response = client.responses.create(
        model=model,
        input=prompt,
        max_output_tokens=max_output_tokens,
    )
    return getattr(response, "output_text", "").strip()


def embed_texts(texts: List[str], model: str, demo_mode: bool = True) -> List[List[float]]:
    """Create embeddings. Demo mode uses deterministic local vectors."""
    if demo_mode:
        from services.rag_service import local_hash_embedding
        return [local_hash_embedding(t) for t in texts]
    client = get_client()
    response = client.embeddings.create(model=model, input=texts)
    return [item.embedding for item in response.data]


def render_openai_error(error: Exception) -> None:
    st.error("The AI request failed.")
    message = str(error)
    if "insufficient_quota" in message or "quota" in message.lower():
        st.info("This usually means API billing/credits are not active or your quota was reached. Try Demo Mode first.")
    elif "model" in message.lower() and "not" in message.lower():
        st.info("The selected model may not be available to your account. Try a smaller/default model.")
    elif "api" in message.lower() and "key" in message.lower():
        st.info("Check your .env file and API key permissions.")
    st.code(message)
