from pydantic import BaseModel, Field
from typing import List, Optional

class Message(BaseModel):
    role: str = Field(..., description="Role of the sender, typically 'user' or 'assistant' or 'system'")
    content: str = Field(..., description="The content of the message")

class ChatRequest(BaseModel):
    model: str = Field(..., description="The name of the Ollama model to use, e.g., 'mistral:7b', 'llama3.2:3b', 'phi3:mini'")
    prompt: Optional[str] = Field(None, description="The latest prompt to send to the model")
    messages: Optional[List[Message]] = Field(default_factory=list, description="Optional history of previous messages")
    temperature: Optional[float] = Field(0.7, description="Sampling temperature between 0.0 and 1.0", ge=0.0, le=1.0)

class ChatResponse(BaseModel):
    answer: str = Field(..., description="The main answer or response to the user's prompt")
    confidence: float = Field(..., description="A confidence score between 0.0 and 1.0 indicating how confident the model is in its answer", ge=0.0, le=1.0)
    reasoning: str = Field(..., description="A brief explanation of how the model arrived at the answer")
