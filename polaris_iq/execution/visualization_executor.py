# execution/visualization_executor.py

import matplotlib.pyplot as plt
import os
import uuid


class VisualizationExecutor:

    def __init__(self, conn, output_dir="generated_plots"):
        self.conn = conn
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def execute(self, plan: dict):

        table = plan["data_scope"]["tables"][0]

        # Check both statistics and prediction for params
        params = None
        if plan.get("statistics") and plan["statistics"].get("parameters"):
            params = plan["statistics"]["parameters"]
        elif plan.get("prediction") and plan["prediction"].get("parameters"):
            params = plan["prediction"]["parameters"]

        if not params:
            raise ValueError("Visualization plan missing parameters in statistics or prediction.")

        x_col = params["x"]
        y_col = params["y"]
        chart_type = params.get("chart_type", "line")

        return self._render(table, x_col, y_col, chart_type)

    def generate_plot(self, x: str, y: str, chart_type: str = "line", table: str = "test_table"):
        """Tool-compatible handler called via ToolExecutor with kwargs."""
        return self._render(table, x, y, chart_type)

    def _render(self, table: str, x_col: str, y_col: str, chart_type: str = "line"):
        """Shared rendering logic."""

        df = self.conn.execute(
            f"SELECT {x_col}, {y_col} FROM {table}"
        ).fetchdf()

        filename = f"{uuid.uuid4().hex}.png"
        filepath = os.path.join(self.output_dir, filename)

        plt.figure()

        if chart_type == "line":
            plt.plot(df[x_col], df[y_col])
        elif chart_type == "scatter":
            plt.scatter(df[x_col], df[y_col])
        elif chart_type == "bar":
            plt.bar(df[x_col], df[y_col])
        else:
            raise ValueError("Unsupported chart type")

        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.title(f"{y_col} vs {x_col}")
        plt.tight_layout()
        plt.savefig(filepath)
        plt.close()

        return {
            "analysis_type": "visualization",
            "chart_type": chart_type,
            "x": x_col,
            "y": y_col,
            "file_path": filepath
        }