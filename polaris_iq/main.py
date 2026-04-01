# main.py

from polaris_iq.core.bootstrap import PolarisEngine
from polaris_iq.core.config import PolarisConfig
from polaris_iq.data_layer.precompute import precompute
from polaris_iq.engine.orchestrator import PolarisOrchestrator
from polaris_iq.execution.adaptive_optimizer import AdaptiveOptimizer
from polaris_iq.execution.cost_estimator import CostEstimator
from polaris_iq.execution.engine_selector import EngineSelector
from polaris_iq.execution.execution_logger import ExecutionLogger
from polaris_iq.execution.execution_router import ExecutionRouter
from polaris_iq.explanation.explanation_engine import ExplanationEngine
from polaris_iq.planning.plan_memory import PlanMemory


def run_test():

    print("\n=== STEP 1: Precomputing Dataset ===")
    precompute(
        input_path=r"C:\Arka\Programming Language\PolarisIQ Project\Data\Salary_dataset.csv",
        table_name="test_table",
        duckdb_path="polaris.db",
    )

    print("Precompute complete.\n")

    print("=== STEP 2: Bootstrapping Engine ===")
    engine = PolarisEngine(PolarisConfig())

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

    print("Engine initialized.\n")

    # ----------------------------------------
    # TEST 1 — Deterministic Analytical Query
    # ----------------------------------------

    print("=== STEP 3: Testing Deterministic Query ===")

    response = orchestrator.handle_query(
        user_query="In how many year of experinence the salary will be equal to mean?",
        table_name="test_table",
    )

    print("\nDeterministic Query Response:")
    print(response)

    # ----------------------------------------
    # TEST 2 — Tool-Based Plot Query
    # ----------------------------------------

    print("\n=== STEP 4: Testing Tool-Based Plot ===")

    tool_response = orchestrator.handle_tool_query(
        user_query="Generate a line plot of revenue vs age", table_name="test_table"
    )

    print("\nTool Query Response:")
    print(tool_response)

    print("\n=== TEST COMPLETE ===")


if __name__ == "__main__":
    run_test()
