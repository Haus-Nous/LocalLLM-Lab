import argparse
import asyncio
import sys
import json
import uvicorn
from app.schemas import ChatRequest
from app.llm_client import generate_response

async def run_cli(model: str, prompt: str):
    request = ChatRequest(model=model, prompt=prompt)
    try:
        response = await generate_response(request)
        # Dump using model_dump to ensure Pydantic parsing gives dictionary
        print(json.dumps(response.model_dump(), indent=2))
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Local AI Assistant CLI")
    parser.add_argument("--model", type=str, help="Model to use (e.g., mistral:7b, llama3.2:3b)")
    parser.add_argument("--prompt", type=str, help="Prompt to send to the model")
    parser.add_argument("--serve", action="store_true", help="Run the FastAPI server")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    
    args = parser.parse_args()
    
    if args.serve:
        print(f"Starting FastAPI server on port {args.port}...")
        uvicorn.run("app.api:app", host="0.0.0.0", port=args.port, reload=True)
    elif args.model and args.prompt:
        asyncio.run(run_cli(args.model, args.prompt))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
