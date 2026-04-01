# polaris_iq/core/bootstrap.py

import duckdb

from polaris_iq.llm.model_loader import PolarisModel
from polaris_iq.execution.visualization_executor import VisualizationExecutor
from polaris_iq.tools.tool_registry import ToolRegistry, VISUALIZATION_SCHEMA, CORRELATION_SCHEMA
from polaris_iq.tools.tool_executor import ToolExecutor


class PolarisEngine:
    def __init__(self, config):

        self.config = config

        # -------------------------------------------------
        # 1️⃣ Create DuckDB connection FIRST
        # -------------------------------------------------

        self.conn = duckdb.connect(config.DUCKDB_PATH)

        # -------------------------------------------------
        # 2️⃣ Load Model
        # -------------------------------------------------

        self.model = PolarisModel(
            model_path=config.MODEL_PATH, n_ctx=config.CONTEXT_SIZE
        )

        # -------------------------------------------------
        # 3️⃣ Initialize Tool System
        # -------------------------------------------------

        self.tool_registry = ToolRegistry()

        self.visualization_executor = VisualizationExecutor(self.conn)

        self.tool_registry.register(
            name="generate_plot",
            handler=self.visualization_executor.generate_plot,
            schema=VISUALIZATION_SCHEMA,
        )

        self.tool_registry.register(
            name="correlation_analysis",
            handler=self.get_correlations_tool,
            schema=CORRELATION_SCHEMA,
        )

        self.tool_executor = ToolExecutor(self.tool_registry)

    def get_correlations_tool(self, table: str = "test_table"):
        try:
            result = self.conn.execute(
                f"SELECT column_x, column_y, correlation FROM polaris_correlations "
                f"WHERE correlation IS NOT NULL AND table_name = '{table}' "
                f"ORDER BY abs(correlation) DESC LIMIT 10"
            ).fetchall()
            correlations = [{"col_x": r[0], "col_y": r[1], "corr": round(r[2], 4)} for r in result]
            return {
                "analysis_type": "correlation_summary",
                "table": table,
                "top_correlations": correlations
            }
        except Exception as e:
            return {"error": str(e)}

    def shutdown(self):
        self.conn.close()

