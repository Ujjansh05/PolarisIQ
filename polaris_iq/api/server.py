# api/server.py

from fastapi import FastAPI

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


app = FastAPI()

# -----------------------------
# Bootstrap Engine
# -----------------------------

engine = PolarisEngine(PolarisConfig())

# -----------------------------
# Initialize Core Components
# -----------------------------

router = ExecutionRouter(engine.conn)
cost_estimator = CostEstimator(engine.conn)
engine_selector = EngineSelector()
adaptive_optimizer = AdaptiveOptimizer(engine.conn)
explanation_engine = ExplanationEngine()
logger = ExecutionLogger(engine.conn)
plan_memory = PlanMemory(engine.conn)

# -----------------------------
# Orchestrator
# -----------------------------

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
)

# -----------------------------
# Endpoints
# -----------------------------


@app.post("/query")
def query(payload: dict):
    return orchestrator.handle_query(payload["query"], payload["table"])
