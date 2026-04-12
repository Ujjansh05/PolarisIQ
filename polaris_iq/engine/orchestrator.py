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
        context = build_llm_context(self.conn, table_name)

        # 1. Plan memory lookup
        stored_plan = self.plan_memory.retrieve(user_query, table_name)

        plan = None
        if stored_plan:
            try:
                candidate_plan = QueryPlan(**stored_plan)
                validate_plan(self.conn, candidate_plan, table_name)
                plan = candidate_plan
            except Exception:
                # Drop stale/invalid cached plans and regenerate.
                try:
                    self.plan_memory.delete(user_query, table_name)
                except Exception:
                    pass

        if plan is None:
            is_valid = False
            used_fallback = False
            try:
                plan = generate_structured_plan(user_query, context, self.model)
                validate_plan(self.conn, plan, table_name)
                is_valid = True
            except Exception:
                # LLM can occasionally return malformed/empty JSON plans (e.g. {}).
                # Fall back to a deterministic safe plan instead of returning HTTP 500.
                plan = self._build_fallback_plan(user_query, table_name)
                is_valid = True
                used_fallback = True

            if is_valid and not used_fallback:
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
        try:
            explanation = self.explanation_engine.generate(
                result,
                plan.explanation_level,
                self.model,
                user_query=user_query,
                context=context,
            )
        except Exception:
            explanation = self._fallback_explanation(result)

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

    @staticmethod
    def _is_visualization_query(user_query: str) -> bool:
        q = (user_query or "").lower()
        keywords = [
            "plot", "chart", "graph", "visual", "visualize",
            "histogram", "scatter", "bar", "line", "pie",
        ]
        return any(k in q for k in keywords)

    @staticmethod
    def _is_correlation_query(user_query: str) -> bool:
        q = (user_query or "").lower()
        keywords = ["correlation", "correlate", "relation", "relationship"]
        return any(k in q for k in keywords)

    def _build_fallback_plan(self, user_query: str, table_name: str) -> QueryPlan:
        if self._is_visualization_query(user_query):
            return QueryPlan(
                intent="visualization",
                data_scope={"tables": [table_name]},
                statistics={"type": ["auto"], "parameters": {"chart_type": "scatter"}},
                execution_engine="visualization",
                explanation_level="brief",
            )

        if self._is_correlation_query(user_query):
            return QueryPlan(
                intent="correlation_analysis",
                data_scope={"tables": [table_name]},
                statistics={"type": ["correlation"], "parameters": {"columns": []}},
                execution_engine="duckdb",
                explanation_level="brief",
            )

        # Safe default: numeric summary aggregation.
        return QueryPlan(
            intent="aggregation",
            data_scope={"tables": [table_name]},
            statistics={"type": ["summary"], "parameters": {}},
            execution_engine="duckdb",
            explanation_level="brief",
        )

    @staticmethod
    def _fallback_explanation(result) -> str:
        if isinstance(result, dict):
            if "error" in result:
                return f"I hit an execution issue: {result['error']}"
            return f"Here is the computed result: {result}"
        return f"Here is the computed result: {result}"

