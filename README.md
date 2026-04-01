# PolarisIQ

**AI-Driven Data Engine**

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
* **CLI-first interface** with interactive REPL

---

## Architecture

```
User Query (CLI / API / Frontend)
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

## Installation

Python 3.10+

```bash
pip install -e .
```

For GPU (CUDA):

```bash
set CMAKE_ARGS=-DGGML_CUDA=on
set FORCE_CMAKE=1
pip install --upgrade llama-cpp-python
```

---

## CLI Usage

### Set your model path

```bash
# Option 1: Environment variable (recommended)
set POLARISIQ_MODEL_PATH=C:\path\to\Qwen2.5-7B.Q4_K_M.gguf

# Option 2: Pass --model-path flag to each command
```

### Ingest data

```bash
polarisiq ingest ./data/sales.csv --table sales
polarisiq ingest ./data/customers.parquet --table customers
```

### Query your data

```bash
polarisiq query "find correlation between age and revenue" --table sales
polarisiq query "perform linear regression with age predicting salary" --table salary_data
polarisiq query "generate a scatter plot of age vs revenue" --table sales --tool
```

### Interactive REPL

```bash
polarisiq shell --table sales

# Inside the shell:
# > show average salary by department
# > /tool                          (toggle visualization mode)
# > generate a line plot of revenue vs age
# > /table customers               (switch table)
# > /quit
```

### List tables

```bash
polarisiq tables
polarisiq tables --schema sales
```

### Start the API server (for the web frontend)

```bash
polarisiq serve --port 8000
```

---

## Supported Data Formats

* `.csv` / `.tsv`
* `.parquet`
* `.json` / `.ndjson`
* `.xlsx` / `.xls`
* `.duckdb`

All data is persisted and processed using **DuckDB (OLAP)**.

---

## Tech Stack

| Layer           | Technology              |
| --------------- | ----------------------- |
| OLAP Engine     | DuckDB                  |
| Data Processing | Polars                  |
| ML Engine       | Scikit-learn            |
| LLM Runtime     | llama-cpp-python        |
| Model           | Qwen2.5 7B (4-bit GGUF) |
| Visualization   | Matplotlib              |
| CLI Framework   | Typer + Rich            |
| API Server      | FastAPI + Uvicorn       |
| Frontend        | React + Vite (optional) |

---

## Example Capabilities

* "Perform linear regression with age predicting revenue."
* "Find correlation between churn probability and revenue."
* "Generate a line plot of revenue vs age."
* "Identify high-value customers and analyze churn risk."

---

## Design Principles

* Deterministic execution
* Strict JSON plan validation
* No raw LLM-generated SQL execution
* Tool-schema enforcement
* Controlled execution loops
* Fully local data processing

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `POLARISIQ_MODEL_PATH` | Path to GGUF model file | *(required)* |
| `POLARISIQ_DB_PATH` | Path to DuckDB database | `polaris.db` |
| `POLARISIQ_CONTEXT_SIZE` | LLM context window size | `4096` |

---

PolarisIQ is designed for developers, data engineers, and researchers who want powerful AI-driven analytics — locally, securely, and under full system control.
