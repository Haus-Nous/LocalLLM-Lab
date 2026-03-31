import time
import csv
import psutil
from datetime import datetime
from ollama import AsyncClient
import asyncio
from typing import List, Dict
import os
import sys

# Add parent directory to path so we can import from evaluation.dataset
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

client = AsyncClient()

def get_ollama_memory() -> float:
    """Returns Ollama process memory in MB."""
    total_mem = 0
    for proc in psutil.process_iter(['name', 'memory_info']):
        try:
            if 'ollama' in proc.info['name'].lower():
                total_mem += proc.info['memory_info'].rss
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return total_mem / (1024 * 1024)

async def measure_performance(model: str, prompt: str) -> Dict:
    start_time = time.time()
    first_token_time = None
    token_count = 0
    
    mem_before = get_ollama_memory()
    
    try:
        stream = await client.generate(
            model=model,
            prompt=prompt,
            stream=True
        )
        async for chunk in stream:
            if first_token_time is None:
                first_token_time = time.time()
            token_count += 1
            
        end_time = time.time()
        mem_after = get_ollama_memory()
        
        ttft = first_token_time - start_time if first_token_time else 0
        total_time = end_time - start_time
        tps = token_count / total_time if total_time > 0 else 0
        
        return {
            "model": model,
            "prompt": prompt[:50] + "...",
            "ttft_sec": round(ttft, 3),
            "total_latency_sec": round(total_time, 3),
            "tokens_per_sec": round(tps, 2),
            "token_count": token_count,
            "memory_before_mb": round(mem_before, 2),
            "memory_after_mb": round(mem_after, 2),
            "memory_diff_mb": round(mem_after - mem_before, 2),
            "status": "success"
        }
    except Exception as e:
        return {
            "model": model,
            "prompt": prompt[:50] + "...",
            "ttft_sec": 0,
            "total_latency_sec": 0,
            "tokens_per_sec": 0,
            "token_count": 0,
            "memory_before_mb": 0,
            "memory_after_mb": 0,
            "memory_diff_mb": 0,
            "status": f"error: {str(e)}"
        }

async def run_benchmarks(models: List[str], prompts: List[str], output_file: str):
    results = []
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    print(f"Starting benchmark on models: {models}")
    for model in models:
        print(f"\\n--- Benchmarking model: {model} ---")
        
        # Warmup
        print("Running warmup...")
        try:
            await measure_performance(model, "Warm up prompt")
        except Exception as e:
            print(f"Warmup failed for {model}: {e}")
            continue
            
        for i, prompt in enumerate(prompts):
            print(f"Prompt {i+1}/{len(prompts)}: {prompt[:30]}...")
            res = await measure_performance(model, prompt)
            results.append(res)
            
    # Save to CSV
    if results:
        keys = results[0].keys()
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(results)
            
        print(f"\\nResults saved to {output_file}")

if __name__ == "__main__":
    from evaluation.dataset import DATASET
    
    # Take a small subset to ensure script runs quickly for demonstration, 
    # but the full 40 prompts can be run by uncommenting.
    test_prompts = [item["prompt"] for item in DATASET[:2]]
    
    models_to_test = ["mistral:7b", "llama3.2:3b", "phi3:mini", "llama3.1:8b", "deepseek-r1:8b"]
    output_csv = f"report/benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    asyncio.run(run_benchmarks(models_to_test, test_prompts, output_csv))
