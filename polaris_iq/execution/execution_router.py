# execution/execution_router.py

from polaris_iq.core.exceptions import ExecutionError


class ExecutionRouter:
    def __init__(self, conn):
        from .visualization_executor import VisualizationExecutor
        from .duckdb_executor import DuckDBExecutor
        from .polars_executor import PolarsExecutor
        from .sklearn_executor import SklearnExecutor

        self.visualization_executor = VisualizationExecutor(conn)
        self.duckdb_executor = DuckDBExecutor(conn)
        self.polars_executor = PolarsExecutor(conn)
        self.sklearn_executor = SklearnExecutor(conn)

    def execute(self, plan: dict, engine: str):

        if engine == "visualization":
            return self.visualization_executor.execute(plan)

        elif engine == "duckdb":
            return self.duckdb_executor.execute(plan)

        elif engine == "polars":
            return self.polars_executor.execute(plan)

        elif engine == "python_sklearn":
            return self.sklearn_executor.execute(plan)

        else:
            raise ExecutionError(f"Unknown execution engine: {engine}")
