# execution/engine_selector.py


class EngineSelector:
    def select(self, plan, cost_info: dict):

        intent = plan.intent
        rows = cost_info["row_count"]

        # Visualization
        if intent == "visualization":
            return "visualization"

        # Aggregations → DuckDB always
        if intent in ["aggregation", "correlation_analysis", "hypothesis_test"]:
            return "duckdb"

        # Regression
        if intent == "regression_analysis":
            if rows > 1_000_000:
                return "duckdb"  # Simple regression via SQL
            return "python_sklearn"

        # Classification
        if intent == "classification":
            return "python_sklearn"

        # Feature engineering
        if intent == "feature_engineering":
            return "polars"

        raise ValueError(f"No engine rule for intent: {intent}")
