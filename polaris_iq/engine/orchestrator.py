# polaris_iq/engine/orchestrator.py

import os
import time

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

        start_time = time.time()

        # 1. Plan memory lookup
        stored_plan = self.plan_memory.retrieve(user_query, table_name)

        if stored_plan:
            plan = QueryPlan(**stored_plan)
            context = build_llm_context(self.conn, table_name)
        else:
            context = build_llm_context(self.conn, table_name)

            plan = generate_structured_plan(user_query, context, self.model)

            # Validate but do not hard-fail — let the executor handle bad plans
            try:
                validate_plan(self.conn, plan, table_name)
            except Exception:
                pass

            self.plan_memory.store(user_query, table_name, plan.model_dump())

        # 2. Cost estimation
        cost_info = self.cost_estimator.estimate(plan, table_name)

        # 3. Rule-based selection
        fallback_engine = self.engine_selector.select(plan, cost_info)

        # 4. Adaptive override
        selected_engine = self.adaptive_optimizer.choose_best_engine(
            plan.intent, fallback_engine
        )

        # 5. Execution
        result = self.router.execute(plan.model_dump(), engine=selected_engine)

        # 6. Logging
        duration = time.time() - start_time
        try:
            row_count = cost_info.get("row_count", 0) if cost_info else 0
            self.logger.log(plan.intent, selected_engine, row_count, duration)
        except Exception:
            pass

        # 7. Explanation — pass user query and context for targeted answers
        explanation = self.explanation_engine.generate(
            result,
            plan.explanation_level,
            self.model,
            user_query=user_query,
            context=context,
        )

        response = {
            "explanation": explanation,
            "metadata": {"intent": plan.intent, "engine_used": selected_engine},
        }

        # 8. Attach image URL if visualization produced a file
        image_url = self._to_image_url(result)
        if image_url:
            response["image_url"] = image_url

        return response

    # -------------------------------------------------
    # Tool-Based Query Mode
    # -------------------------------------------------

    def handle_tool_query(self, user_query: str, table_name: str):

        if not self.tool_executor:
            raise RuntimeError("Tool executor not configured. Pass tool_executor to PolarisOrchestrator.")

        context = build_llm_context(self.conn, table_name)

        agent = ToolAgent(self.model, self.tool_executor)

        result = agent.run(user_query, context)

        response = {
            "tool_result": result,
            "metadata": {"mode": "tool_agent", "table": table_name},
        }

        # Attach image URL if tool produced a visualization file
        image_url = self._to_image_url(result)
        if image_url:
            response["image_url"] = image_url

        return response

    # -------------------------------------------------
    # Helpers
    # -------------------------------------------------

    @staticmethod
    def _to_image_url(result) -> str | None:
        """Extract image URL from a result dict containing a file_path."""
        if not isinstance(result, dict):
            return None
        file_path = result.get("file_path")
        if not file_path:
            return None
        filename = os.path.basename(file_path)
        return f"/plots/{filename}"

