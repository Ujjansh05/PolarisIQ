# execution/polars_executor.py

import polars as pl
from polaris_iq.core.exceptions import ExecutionError


class PolarsExecutor:
    def __init__(self, conn):
        self.conn = conn

    def execute(self, plan: dict):

        table = plan["data_scope"]["tables"][0]
        arrow_table = self.conn.execute(f"SELECT * FROM {table}").arrow()

        df = pl.from_arrow(arrow_table)

        intent = plan["intent"]

        if intent == "feature_engineering":
            # Extend with real ops
            return {"analysis_type": "feature_engineering", "rows": df.shape[0]}

        raise ExecutionError(f"Polars does not support intent: {intent}")
