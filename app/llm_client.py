import json
import logging
from typing import Optional, List
from ollama import AsyncClient
from pydantic import ValidationError
from .schemas import ChatRequest, ChatResponse, Message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = AsyncClient()

SYSTEM_PROMPT = """You are a helpful AI assistant. You must ALWAYS return your answer strictly as a JSON object matching the following schema:
{
    "answer": "your main response here",
    "confidence": 0.95,
    "reasoning": "brief explanation of how you arrived at this answer"
}
Do not include any other text or markdown formatting outside the JSON block.
"""

async def generate_response(request: ChatRequest, temperature: Optional[float] = None) -> ChatResponse:
    """
    Generates a response from the Ollama model enforcing JSON schema.
    If validation fails, retries once with a corrected prompt.
    """
    prompt = request.prompt
    model = request.model
    messages = request.messages
    
    # Use request body temperature if specific temperature not passed to function
    if temperature is None:
        temperature = request.temperature
    
    try:
        response_text = await _call_ollama(model, prompt, temperature, messages)
        return _parse_and_validate(response_text)
    except (json.JSONDecodeError, ValidationError) as e:
        logger.warning(f"Initial validation failed: {str(e)}. Retrying...")
        
        # Retry with an even stricter prompt
        retry_prompt = (
            f"Your previous response was invalid JSON. You must return EXACTLY AND ONLY a JSON object matching the schema.\n\n"
            f"Original prompt: {prompt}\n\n"
            f"Error details: {str(e)}"
        )
        try:
            retry_response = await _call_ollama(model, retry_prompt, temperature, messages)
            return _parse_and_validate(retry_response)
        except Exception as retry_e:
            logger.error(f"Retry validation failed: {str(retry_e)}")
            raise ValueError(f"Failed to generate valid JSON response after retry: {str(retry_e)}")

async def _call_ollama(model: str, prompt: Optional[str], temperature: float, messages: Optional[List[Message]] = None) -> str:
    api_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    if messages:
        for msg in messages:
            api_messages.append({"role": msg.role, "content": msg.content})
            
    if prompt:
        api_messages.append({"role": "user", "content": prompt})

    response = await client.chat(
        model=model,
        messages=api_messages,
        format="json",  # Force Ollama to return JSON
        options={"temperature": temperature}
    )
    return response['message']['content']

def _parse_and_validate(content: str) -> ChatResponse:
    # Sometimes models wrap JSON in markdown block even with format="json"
    content = content.strip()
    if content.startswith("```json"):
        content = content[7:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()
    
    data = json.loads(content)
    return ChatResponse(**data)
