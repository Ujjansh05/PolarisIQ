# polaris_iq/core/bootstrap.py

import duckdb

from polaris_iq.llm.model_loader import PolarisModel
from polaris_iq.execution.visualization_executor import VisualizationExecutor
from polaris_iq.tools.tool_registry import ToolRegistry, VISUALIZATION_SCHEMA
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

        self.tool_executor = ToolExecutor(self.tool_registry)

    def shutdown(self):
        self.conn.close()
