# polaris_iq/cli/engine.py
# Lazy engine bootstrap shared across CLI commands.

import os
from pathlib import Path
from polaris_iq.cli.display import console, print_error, create_progress, REASONING_STEPS


DEFAULT_DB_PATH = "polaris.db"


def resolve_model_path(model_path: str | None = None) -> str:
    """Resolve model path from argument, env var, or raise."""

    path = model_path or os.environ.get("POLARISIQ_MODEL_PATH")

    if not path:
        print_error(
            "No model path provided.\n"
            "Set POLARISIQ_MODEL_PATH env var or pass --model-path flag."
        )
        raise SystemExit(1)

    if not Path(path).exists():
        print_error(f"Model file not found: {path}")
        raise SystemExit(1)

    return path


def resolve_db_path(db_path: str | None = None) -> str:
    """Resolve DuckDB path from argument, env var, or default."""

    return db_path or os.environ.get("POLARISIQ_DB_PATH", DEFAULT_DB_PATH)


def bootstrap_engine(model_path: str, db_path: str):
    """Bootstrap the full PolarisIQ engine stack and return the orchestrator."""

    from polaris_iq.core.config import PolarisConfig
    from polaris_iq.core.bootstrap import PolarisEngine
    from polaris_iq.engine.orchestrator import PolarisOrchestrator
    from polaris_iq.execution.execution_router import ExecutionRouter
    from polaris_iq.execution.cost_estimator import CostEstimator
    from polaris_iq.execution.engine_selector import EngineSelector
    from polaris_iq.execution.adaptive_optimizer import AdaptiveOptimizer
    from polaris_iq.execution.execution_logger import ExecutionLogger
    from polaris_iq.explanation.explanation_engine import ExplanationEngine
    from polaris_iq.planning.plan_memory import PlanMemory

    progress = create_progress()

    with progress:
        task = progress.add_task("Loading LLM model...", total=len(REASONING_STEPS))

        config = PolarisConfig()
        config.MODEL_PATH = model_path
        config.DUCKDB_PATH = db_path

        engine = PolarisEngine(config)
        progress.update(task, advance=2, description="Initializing execution engines...")

        router = ExecutionRouter(engine.conn)
        cost_estimator = CostEstimator(engine.conn)
        engine_selector = EngineSelector()
        adaptive_optimizer = AdaptiveOptimizer(engine.conn)
        explanation_engine = ExplanationEngine()
        logger = ExecutionLogger(engine.conn)
        plan_memory = PlanMemory(engine.conn)
        progress.update(task, advance=2, description="Building orchestrator...")

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
        progress.update(task, advance=2, description="Ready.")

    return orchestrator, engine
