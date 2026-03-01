# execution/duckdb_executor.py

from polaris_iq.core.exceptions import ExecutionError


class DuckDBExecutor:
    def __init__(self, conn):
        self.conn = conn

    def execute(self, plan: dict):

        intent = plan["intent"]

        if intent == "aggregation":
            sql = plan["statistics"]["parameters"]["sql"]
            return self.conn.execute(sql).fetchdf().to_dict()

        if intent == "correlation_analysis":
            col_x, col_y = plan["statistics"]["parameters"]["columns"]
            table = plan["data_scope"]["tables"][0]

            result = self.conn.execute(
                f"SELECT corr({col_x}, {col_y}) FROM {table}"
            ).fetchone()[0]

            return {"analysis_type": "correlation", "correlation": float(result)}

        raise ExecutionError(f"DuckDB does not support intent: {intent}")
