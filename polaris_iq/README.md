# PolarisIQ

**AI-Driven Data Engine (Phase 7)**

PolarisIQ is a **local, GPU-accelerated analytical intelligence engine** that converts natural language queries into structured data analysis, machine learning workflows, and visualizations — all running on your local system.

Built on DuckDB, Polars, Scikit-learn, and Qwen2.5 (GGUF via llama-cpp), PolarisIQ delivers deterministic, cost-aware, and tool-controlled analytics without relying on cloud services.

---

## Key Features

* Natural language → structured analytical execution
* Aggregation, correlation, regression, classification
* Built-in graph generation (line, scatter, bar)
* Cost-aware execution routing
* Autonomous multi-step workflows
* Tool-calling agent architecture
* Plan caching + adaptive engine optimization
* Fully local execution (no external API calls)

---

## 🏗 Architecture

```
User Query
    ↓
LLM Planning (Structured JSON)
    ↓
Validation
    ↓
Cost-Based Engine Selection
    ↓
Execution (DuckDB / Sklearn / Polars / Visualization)
    ↓
Explanation
```

PolarisIQ separates planning, execution, and explanation to ensure deterministic and secure analytical workflows.

---

## 📂 Supported Data Formats

* `.csv` / `.tsv`
* `.parquet`
* `.json` / `.ndjson`
* `.xlsx` / `.xls`
* `.duckdb`

All data is persisted and processed using **DuckDB (OLAP)**.

---

## 🧩 Tech Stack

| Layer           | Technology              |
| --------------- | ----------------------- |
| OLAP Engine     | DuckDB                  |
| Data Processing | Polars                  |
| ML Engine       | Scikit-learn            |
| LLM Runtime     | llama-cpp-python        |
| Model           | Qwen2.5 7B (4-bit GGUF) |
| Visualization   | Matplotlib              |

---

## ⚙ Installation

Python 3.10+

```bash
pip install duckdb polars pyarrow pandas numpy scikit-learn \
llama-cpp-python matplotlib fastapi uvicorn
```

For GPU (CUDA):

```bash
set CMAKE_ARGS=-DGGML_CUDA=on
set FORCE_CMAKE=1
pip install --upgrade llama-cpp-python
```

---

## ▶ Running PolarisIQ

From the project root (one level above `polaris_iq/`):

```bash
python -m polaris_iq.main
```

---

## 📊 Example Capabilities

* “Perform linear regression with age predicting revenue.”
* “Find correlation between churn probability and revenue.”
* “Generate a line plot of revenue vs age.”
* “Identify high-value customers and analyze churn risk.”

---

## 🔒 Design Principles

* Deterministic execution
* Strict JSON plan validation
* No raw LLM-generated SQL execution
* Tool-schema enforcement
* Controlled execution loops
* Fully local data processing

---

## 🎯 Project Status

PolarisIQ is complete through **Phase 7**:

✔ Deterministic analytical engine
✔ Autonomous multi-step workflows
✔ Tool-calling agent system
✔ Visualization support
✔ Adaptive execution optimization

---

PolarisIQ is designed for developers, data engineers, and researchers who want powerful AI-driven analytics — locally, securely, and under full system control.
