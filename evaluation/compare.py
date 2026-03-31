import sys
import os
import asyncio
from typing import List
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.llm_client import generate_response
from app.schemas import ChatRequest
from evaluation.dataset import DATASET

async def compare_models(models: List[str], num_prompts: int = 5, temperature: float = 0.7):
    """
    Runs a subset of prompts through multiple models to compare qualitative outputs.
    Saves outputs to a JSON or markdown report.
    """
    
    prompts = [item["prompt"] for item in DATASET[:num_prompts]]
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "temperature": temperature,
        "results": []
    }
    
    print(f"Comparing models: {models} at temperature {temperature}")
    
    for prompt in prompts:
        print(f"\\nEvaluating prompt: {prompt}")
        prompt_result = {
            "prompt": prompt,
            "models": {}
        }
        
        for model in models:
            req = ChatRequest(model=model, prompt=prompt)
            print(f"  -> Sending to {model}...")
            try:
                response = await generate_response(req, temperature=temperature)
                prompt_result["models"][model] = {
                    "answer": response.answer,
                    "confidence": response.confidence,
                    "reasoning": response.reasoning,
                    "status": "success"
                }
            except Exception as e:
                prompt_result["models"][model] = {
                    "status": f"error: {str(e)}"
                }
                
        report["results"].append(prompt_result)

    # Convert dictionary report to a markdown summary
    md_report = f"# Model Comparison Report\\n\\n"
    md_report += f"- **Date:** {report['timestamp']}\\n"
    md_report += f"- **Temperature:** {temperature}\\n"
    md_report += f"- **Models tested:** {', '.join(models)}\\n\\n"
    
    for res in report["results"]:
        md_report += f"## Prompt: {res['prompt']}\\n\\n"
        for model, out in res['models'].items():
            md_report += f"### {model}\\n"
            if out["status"] == "success":
                md_report += f"**Confidence:** {out['confidence']}\\n\\n"
                md_report += f"**Reasoning:** {out['reasoning']}\\n\\n"
                md_report += f"**Answer:** {out['answer']}\\n\\n"
            else:
                md_report += f"**Error:** {out['status']}\\n\\n"
        md_report += "---\\n\\n"
        
    os.makedirs("report", exist_ok=True)
    filename = f"report/comparison_temp_{str(temperature).replace('.', '')}.md"
    with open(filename, "w") as f:
        f.write(md_report)
        
    print(f"\\nReport saved to {filename}")

if __name__ == "__main__":
    models_to_test = ["mistral:7b", "llama3.2:3b", "phi3:mini", "llama3.1:8b", "deepseek-r1:8b"]
    # Run comparison at temp 0.7
    print("Running Temp 0.7 experiments...")
    asyncio.run(compare_models(models_to_test, num_prompts=3, temperature=0.7))
    print("\\nRunning Temp 0.0 experiments...")
    asyncio.run(compare_models(models_to_test, num_prompts=3, temperature=0.0))
