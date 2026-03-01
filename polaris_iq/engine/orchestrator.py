# polaris_iq/engine/orchestrator.py

from polaris_iq.engine.tool_agent import ToolAgent
from polaris_iq.planning.context_builder import build_llm_context
from polaris_iq.planning.plan_generator import generate_structured_plan
from polaris_iq.planning.plan_schema import QueryPlan
from polaris_iq.planning.plan_validator import validate_plan


class PolarisOrchestrator:
    def __init__(
        self,
        conn,
        model,
        router,
        cost_estimator,
        engine_selector,
        adaptive_optimizer,
        explanation_engine,
        logger,
        plan_memory,
        tool_executor=None,
    ):
        self.conn = conn
        self.model = model
        self.router = router
        self.cost_estimator = cost_estimator
        self.engine_selector = engine_selector
        self.adaptive_optimizer = adaptive_optimizer
        self.explanation_engine = explanation_engine
        self.logger = logger
        self.plan_memory = plan_memory
        self.tool_executor = tool_executor

    # -------------------------------------------------
    # Deterministic Query Mode
    # -------------------------------------------------

    def handle_query(self, user_query: str, table_name: str):

        # 1️⃣ Plan memory lookup
        stored_plan = self.plan_memory.retrieve(user_query)

        if stored_plan:
            plan = QueryPlan(**stored_plan)
        else:
            context = build_llm_context(self.conn, table_name)

            plan = generate_structured_plan(user_query, context, self.model)

            validate_plan(self.conn, plan, table_name)

            self.plan_memory.store(user_query, plan.model_dump())

        # 2️⃣ Cost estimation
        cost_info = self.cost_estimator.estimate(plan, table_name)

        # 3️⃣ Rule-based selection
        fallback_engine = self.engine_selector.select(plan, cost_info)

        # 4️⃣ Adaptive override
        selected_engine = self.adaptive_optimizer.choose_best_engine(
            plan.intent, fallback_engine
        )

        # 5️⃣ Execution
        result = self.router.execute(plan.model_dump(), engine=selected_engine)

        # 6️⃣ Explanation
        explanation = self.explanation_engine.generate(
            result, plan.explanation_level, self.model
        )

        return {
            "explanation": explanation,
            "metadata": {"intent": plan.intent, "engine_used": selected_engine},
        }

    # -------------------------------------------------
    # Tool-Based Query Mode
    # -------------------------------------------------

    def handle_tool_query(self, user_query: str, table_name: str):

        if not self.tool_executor:
            raise RuntimeError("Tool executor not configured. Pass tool_executor to PolarisOrchestrator.")

        context = build_llm_context(self.conn, table_name)

        agent = ToolAgent(self.model, self.tool_executor)

        result = agent.run(user_query, context)

        return {
            "tool_result": result,
            "metadata": {"mode": "tool_agent", "table": table_name},
        }
