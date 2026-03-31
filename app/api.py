import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .schemas import ChatRequest, ChatResponse
from .llm_client import generate_response

app = FastAPI(title="Local AI Assistant API", description="API for local LLM inference with structured outputs")

# Static files setup
frontend_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(frontend_dir, exist_ok=True)

app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/")
async def serve_index():
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Frontend not found"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        response = await generate_response(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")
