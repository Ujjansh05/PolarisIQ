# polaris_iq/api/server.py

import os
import tempfile
import time
import threading
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from polaris_iq.core.bootstrap import PolarisEngine
from polaris_iq.core.config import PolarisConfig
from polaris_iq.engine.orchestrator import PolarisOrchestrator
from polaris_iq.execution.execution_router import ExecutionRouter
from polaris_iq.execution.cost_estimator import CostEstimator
from polaris_iq.execution.engine_selector import EngineSelector
from polaris_iq.execution.adaptive_optimizer import AdaptiveOptimizer
from polaris_iq.execution.execution_logger import ExecutionLogger
from polaris_iq.explanation.explanation_engine import ExplanationEngine
from polaris_iq.planning.plan_memory import PlanMemory


app = FastAPI(title="PolarisIQ API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve generated plot images as static files
_plots_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "generated_plots")
os.makedirs(_plots_dir, exist_ok=True)
app.mount("/plots", StaticFiles(directory=_plots_dir), name="plots")

# Threading lock for DuckDB (not thread-safe by default)
_db_lock = threading.Lock()

# Bootstrap Engine
config = PolarisConfig()
engine = PolarisEngine(config)

router = ExecutionRouter(engine.conn)
cost_estimator = CostEstimator(engine.conn)
engine_selector = EngineSelector()
adaptive_optimizer = AdaptiveOptimizer(engine.conn)
explanation_engine = ExplanationEngine()
logger = ExecutionLogger(engine.conn)
plan_memory = PlanMemory(engine.conn)

orchestrator = PolarisOrchestrator(
    conn=engine.conn,
    model=engine.model,
    router=router,
    cost_estimator=cost_estimator,
    engine_selector=engine_selector,
    adaptive_optimizer=adaptive_optimizer,
    explanation_engine=explanation_engine,
    logger=logger,
    plan_memory=plan_memory,
    tool_executor=engine.tool_executor,
)

_start_time = time.time()


# ── Health ───────────────────────────────────────────────────────

@app.get("/health")
def health():
    uptime = time.time() - _start_time
    return {
        "status": "online",
        "uptime_seconds": round(uptime, 1),
        "model_loaded": engine.model is not None,
        "db_path": config.DUCKDB_PATH,
    }


# ── Query ────────────────────────────────────────────────────────

@app.post("/query")
def query(payload: dict):
    with _db_lock:
        try:
            result = orchestrator.handle_query(payload["query"], payload["table"])
            return result
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=str(e))



@app.post("/tool-query")
def tool_query(payload: dict):
    with _db_lock:
        try:
            result = orchestrator.handle_tool_query(payload["query"], payload["table"])
            return result
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=str(e))



# ── Tables ───────────────────────────────────────────────────────

INTERNAL_TABLES = {
    "polaris_metadata", "polaris_statistics", "polaris_correlations",
    "polaris_execution_log", "polaris_plan_memory", "execution_log",
}


@app.get("/tables")
def list_tables():
    with _db_lock:
        rows = engine.conn.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'main' AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """).fetchall()

        tables = []
        for (name,) in rows:
            if name in INTERNAL_TABLES:
                continue
            try:
                row_count = engine.conn.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
                col_count = len(engine.conn.execute(f"DESCRIBE {name}").fetchall())
            except Exception:
                row_count = 0
                col_count = 0
            tables.append({
                "name": name,
                "rows": row_count,
                "columns": col_count,
            })

        return {"tables": tables}


@app.get("/tables/{table_name}/schema")
def table_schema(table_name: str):
    with _db_lock:
        try:
            cols = engine.conn.execute(f"DESCRIBE {table_name}").fetchall()
        except Exception:
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")

        columns = []
        for col in cols:
            col_name = col[0]
            col_type = col[1]
            nullable = col[3] == "YES" if len(col) > 3 else True
            columns.append({
                "name": col_name,
                "type": col_type,
                "nullable": nullable,
            })

        try:
            metadata = engine.conn.execute(f"""
                SELECT column_name, null_ratio
                FROM polaris_metadata
                WHERE table_name = '{table_name}'
            """).fetchall()
            null_map = {row[0]: round(row[1] * 100, 2) for row in metadata}
            for col in columns:
                col["null_percent"] = null_map.get(col["name"], 0.0)
        except Exception:
            pass

        row_count = engine.conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]

        return {
            "table_name": table_name,
            "columns": columns,
            "row_count": row_count,
        }


@app.get("/tables/{table_name}/preview")
def table_preview(table_name: str, limit: int = 50):
    with _db_lock:
        try:
            result = engine.conn.execute(f"SELECT * FROM {table_name} LIMIT {limit}").fetchall()
            col_names = [desc[0] for desc in engine.conn.description]
        except Exception:
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")

        rows = [dict(zip(col_names, row)) for row in result]
        return {"table_name": table_name, "columns": col_names, "rows": rows, "total": len(rows)}


# ── Ingest ───────────────────────────────────────────────────────

SUPPORTED_EXTENSIONS = {".csv", ".tsv", ".parquet", ".json", ".ndjson", ".xlsx", ".xls"}


@app.post("/ingest")
async def ingest_file(
    file: UploadFile = File(...),
    table_name: str = Form(None),
):
    ext = Path(file.filename).suffix.lower()

    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: {ext}. Supported: {', '.join(SUPPORTED_EXTENSIONS)}",
        )

    name = table_name or Path(file.filename).stem.replace(" ", "_").replace("-", "_").lower()

    # Save uploaded file to temp
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        from polaris_iq.data_layer.precompute import precompute
        precompute(input_path=tmp_path, table_name=name, duckdb_path=config.DUCKDB_PATH)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingest failed: {e}")
    finally:
        os.unlink(tmp_path)

    row_count = engine.conn.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
    col_count = len(engine.conn.execute(f"DESCRIBE {name}").fetchall())

    return {
        "status": "success",
        "table_name": name,
        "rows": row_count,
        "columns": col_count,
    }


# ── Stats / Logs ─────────────────────────────────────────────────

@app.get("/stats")
def dashboard_stats():
    with _db_lock:
        rows = engine.conn.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'main' AND table_type = 'BASE TABLE'
        """).fetchall()
        user_tables = [r[0] for r in rows if r[0] not in INTERNAL_TABLES]

        total_rows = 0
        for t in user_tables:
            try:
                total_rows += engine.conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            except Exception:
                pass

        query_count = 0
        try:
            query_count = engine.conn.execute(
                "SELECT COUNT(*) FROM polaris_execution_log"
            ).fetchone()[0]
        except Exception:
            pass

        avg_latency = 0.0
        try:
            result = engine.conn.execute(
                "SELECT AVG(execution_time) FROM polaris_execution_log"
            ).fetchone()[0]
            avg_latency = round(result * 1000, 1) if result else 0.0
        except Exception:
            pass

        return {
            "table_count": len(user_tables),
            "total_rows": total_rows,
            "query_count": query_count,
            "avg_latency_ms": avg_latency,
            "uptime_seconds": round(time.time() - _start_time, 1),
        }


@app.get("/logs")
def execution_logs(limit: int = 50):
    with _db_lock:
        logs = []
        try:
            rows = engine.conn.execute(f"""
                SELECT timestamp, intent, engine, row_count, execution_time
                FROM polaris_execution_log
                ORDER BY timestamp DESC
                LIMIT {limit}
            """).fetchall()

            for row in rows:
                logs.append({
                    "timestamp": str(row[0]),
                    "intent": row[1],
                    "engine": row[2],
                    "row_count": row[3],
                    "execution_time_ms": round(row[4] * 1000, 1) if row[4] else 0,
                })
        except Exception:
            pass

        return {"logs": logs}


# ── Profiling Data ───────────────────────────────────────────────

@app.get("/correlations/{table_name}")
def table_correlations(table_name: str):
    with _db_lock:
        correlations = []
        try:
            rows = engine.conn.execute(f"""
                SELECT column_x, column_y, correlation
                FROM polaris_correlations
                WHERE table_name = '{table_name}'
            """).fetchall()

            for row in rows:
                correlations.append({
                    "column_x": row[0],
                    "column_y": row[1],
                    "correlation": round(row[2], 4) if row[2] else None,
                })
        except Exception:
            pass

        return {"table_name": table_name, "correlations": correlations}


@app.get("/statistics/{table_name}")
def table_statistics(table_name: str):
    with _db_lock:
        statistics = []
        try:
            rows = engine.conn.execute(f"""
                SELECT column_name, mean, std, min, max
                FROM polaris_statistics
                WHERE table_name = '{table_name}'
            """).fetchall()

            for row in rows:
                statistics.append({
                    "column": row[0],
                    "mean": round(row[1], 4) if row[1] else None,
                    "std": round(row[2], 4) if row[2] else None,
                    "min": round(row[3], 4) if row[3] else None,
                    "max": round(row[4], 4) if row[4] else None,
                })
        except Exception:
            pass

        return {"table_name": table_name, "statistics": statistics}
