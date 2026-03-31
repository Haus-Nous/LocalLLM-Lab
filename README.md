# Local AI Assistant

A production-quality AI Assistant that runs completely offline using Ollama and Small Language Models (SLMs) such as Llama3.2 (3B), Llama3.1 (8B), Mistral (7B), DeepSeek-R1 (8B), and Phi-3 (Mini). This project demonstrates local LLM inference, structured output generation, dynamic validation and retries, benchmarking, and model comparison.

## 🚀 Features

* **Offline Local Inference:** Absolute privacy with no API calls to third-party providers.
* **Structured Outputs:** The models are forced to return valid JSON with specific formatting using strict prompting and programmatic validation.
* **Validation & Retry:** Robust API using Pydantic; safely handles malformed JSON by systematically retrying with corrected prompts.
* **Extensive Benchmarking:** Measures Time To First Token (TTFT), Tokens Per Second (TPS), Latency, and Memory Footprint across models.
* **Temperature Analysis:** Evaluates output diversity using `temperature=0.0` vs `temperature=0.7`.
* **FastAPI Server:** Exposes a robust local API (`/chat`).
* **CLI Tooling:** Talk to models instantly from the terminal.

---

## 🛠️ Setup & Requirements

1. **Install Ollama**  
   Download and install from [Ollama's official website](https://ollama.com). Ensure the desktop app/daemon is running.
2. **Pull the Models**  
   ```bash
   ollama pull mistral:7b
   ollama pull llama3.2:3b
   ollama pull phi3:mini
   ollama pull llama3.1:8b
   ollama pull deepseek-r1:8b
   ```
3. **Environment Setup**  
   From the `LocalLLM-Lab` directory:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

---

## 💻 Running the System

### 1. CLI Usage
You can run a quick prompt against a model via the terminal:
```bash
python assistant.py --model mistral:7b --prompt "Explain backpropagation simply"
```
The output will be structured JSON.

### 2. API Server
Start the FastAPI server:
```bash
python assistant.py --serve --port 8000
```
Once the server is running, you can access the frontend UI in your browser at: **http://localhost:8000**

Then send a `POST` request to `/chat`:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"model": "llama3.2:3b", "prompt": "What is Python?"}'
```

---

## 📊 Benchmarking Results & Insights

### Performance Metrics (Sample findings on M-series Mac)
* **mistral:7b**: Best reasoning capabilities but slowest TPS (~25-30 TPS). Highest memory footprint (~4.5 GB).
* **llama3.2:3b**: Incredibly fast Time To First Token (TTFT < 0.2s) and high throughput (~60+ TPS) while maintaining near 7B-class reasoning quality.
* **phi3:mini**: Excellent instruction following, very low memory footprint (~2.5 GB), very high TPS.
* **llama3.1:8b**: Balanced performance and reasoning.
* **deepseek-r1:8b**: Strong reasoning model.

### Qualitative Comparison Insights & Temperature
By running the `evaluation/compare.py` script:
* **Temperature 0.0**: Models act extremely deterministically. Best for strict structured schemas, math, and code generation.
* **Temperature 0.7**: Models produce more varied, "creative" outputs. Slightly higher risk of hallucination or malformed JSON (though caught by our retry logic).

---

## 🔒 The Case for Local Inference
* **Absolute Privacy**: Sensitive data (like proprietary source code or PII) never leaves your physical hardware. 
* **Zero Latency "Network" Overhead**: No internet dependency means TTFT relies entirely on disk/RAM speeds, eliminating cloud API jitter.
* **Zero Variable Cost**: Once the hardware is acquired, running millions of tokens costs exactly \$0 in API usage fees. Perfect for scalable, unmetered experimentation.
* **Predictable Constraints**: By comparing 3B vs 7B models, we establish a strict spectrum of speed vs quality, allowing application routing logic to dynamically choose smaller, faster models for simple tasks (like summarization) and larger models for complex logic. 
