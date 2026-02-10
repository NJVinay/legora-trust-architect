"""
Azure OpenAI Client Service.

Handles all LLM interactions via the Azure OpenAI API.
Provides structured output parsing using Pydantic models.
"""

from openai import AzureOpenAI
from typing import Optional
import json
import logging

from app.core.config import get_settings
from app.models.constraints import AgentOutput

logger = logging.getLogger(__name__)

# Module-level client (lazy-initialized)
_client: Optional[AzureOpenAI] = None


def get_client() -> AzureOpenAI:
    """Get or create the Azure OpenAI client."""
    global _client
    if _client is None:
        settings = get_settings()
        _client = AzureOpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        )
    return _client


def generate_completion(
    system_prompt: str,
    user_prompt: str,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
) -> str:
    """
    Send a chat completion request to Azure OpenAI.
    
    Returns the raw text response from the LLM.
    """
    settings = get_settings()
    client = get_client()

    response = client.chat.completions.create(
        model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature or settings.LLM_TEMPERATURE,
        max_tokens=max_tokens or settings.LLM_MAX_TOKENS,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content
    logger.info(
        "LLM response received: %d tokens used",
        response.usage.total_tokens if response.usage else 0,
    )
    return content or ""


def generate_structured_output(
    system_prompt: str,
    user_prompt: str,
    temperature: Optional[float] = None,
) -> AgentOutput:
    """
    Generate a structured AgentOutput from the LLM.
    
    The LLM is instructed to return JSON conforming to the AgentOutput schema.
    This function parses the JSON and validates it against the Pydantic model.
    
    Raises:
        ValueError: If the LLM response cannot be parsed as valid AgentOutput.
    """
    raw = generate_completion(system_prompt, user_prompt, temperature)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM returned invalid JSON: {e}")

    try:
        output = AgentOutput.model_validate(data)
    except Exception as e:
        raise ValueError(f"LLM output failed schema validation: {e}")

    return output
