# Lab 3: Chatbot vs ReAct Agent (Industry Edition)

Welcome to Phase 3 of the Agentic AI course! This lab focuses on moving from a simple LLM Chatbot to a sophisticated **ReAct Agent** with industry-standard monitoring.

## 🚀 Getting Started

### 1. Setup Environment
Copy the `.env.example` to `.env` and fill in your API keys:
```bash
cp .env.example .env
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Directory Structure
- `src/tools/`: Extension point for your custom tools.
- `src/telemetry/`: Logging and metrics tracking.
- `src/agent/`: Core ReAct loop logic.
- `logs/`: Automatically generated traces and benchmark results.

---

## 🖥️ Running the Interactive Dashboard (Streamlit)

To interactively compare the Baseline LLM with the ReAct Agent, use the included Streamlit UI. 

**Important:** Do *not* use `python app.py`. You must run it via the streamlit CLI:
```bash
streamlit run app.py
```
This will launch a local web server (usually at `http://localhost:8501`). The dashboard includes:
- **Two Tabs:** Toggle between the ReAct Agent (Tools enabled) and Baseline Chatbot (No Tools).
- **Latency & Step Tracking:** Visual badges showing execution time and reasoning steps.
- **Quick Test Cases:** A sidebar with predefined prompts to instantly test Happy Paths, Negative Paths, and Out-of-Domain queries.

---

## 📊 Running Automated Benchmarks

To systematically evaluate the performance, hallucination rate, and token usage across multiple test cases without manual clicking, run the automated benchmark script:

```bash
python benchmark.py
```

**What this does:**
1. Executes a suite of 12 robust test cases (including out-of-domain queries like math and weather, and negative paths like requesting non-existent books).
2. Clears the context history between each query to ensure zero-shot accuracy.
3. Prints a clean comparative table in your terminal showing Latency and Steps.
4. Appends rich telemetry data (Tokens used, completion status, tools invoked) to `logs/benchmark_results.json`.
