# execution/visualization_executor.py

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os
import uuid


class VisualizationExecutor:

    def __init__(self, conn, output_dir="generated_plots"):
        self.conn = conn
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def execute(self, plan: dict):

        tables = (plan.get("data_scope") or {}).get("tables") or []
        if not tables:
            raise ValueError("Visualization plan missing table in data_scope.")

        table = tables[0]

        # Collect parameters from statistics or prediction (whichever has them)
        params = self._extract_params(plan)

        # Extract x, y, and chart_type from various possible key names
        x_col = self._get_column(params, ["x", "x_col", "x_column", "independent", "column_x"])
        y_col = self._get_column(params, ["y", "y_col", "y_column", "dependent", "column_y"])
        chart_type = (
            params.get("chart_type")
            or params.get("type")
            or params.get("plot_type")
            or "scatter"
        )

        # If columns are lists, take the first element
        if isinstance(x_col, list):
            x_col = x_col[0] if x_col else None
        if isinstance(y_col, list):
            y_col = y_col[0] if y_col else None

        # Auto-detect columns if not specified
        if not x_col or not y_col:
            x_col, y_col = self._auto_detect_columns(table, x_col, y_col)

        return self._render(table, x_col, y_col, chart_type)

    def generate_plot(self, x: str, y: str, chart_type: str = "line", table: str = "test_table"):
        """Tool-compatible handler called via ToolExecutor with kwargs."""
        return self._render(table, x, y, chart_type)

    def _extract_params(self, plan: dict) -> dict:
        """Extract parameters from statistics or prediction, with fallbacks."""
        stats = plan.get("statistics") or {}
        pred = plan.get("prediction") or {}

        params = stats.get("parameters") or pred.get("parameters") or {}

        # Also check for columns/group_by at the statistics level
        if not params and isinstance(stats, dict):
            params = {k: v for k, v in stats.items() if k != "type"}

        return params

    def _get_column(self, params: dict, keys: list):
        """Try multiple possible key names to get a column value."""
        for key in keys:
            val = params.get(key)
            if val is not None:
                return val
        return None

    def _auto_detect_columns(self, table: str, x_col=None, y_col=None):
        """Auto-detect x/y columns from the table schema when not specified."""
        try:
            cols = self.conn.execute(f"DESCRIBE {table}").fetchall()
        except Exception:
            raise ValueError(f"Cannot describe table '{table}' to auto-detect columns.")

        numeric_cols = [
            c[0] for c in cols
            if any(t in c[1].upper() for t in ["INT", "FLOAT", "DOUBLE", "DECIMAL", "BIGINT", "NUMERIC"])
        ]
        all_cols = [c[0] for c in cols]

        if not x_col and not y_col:
            if len(numeric_cols) >= 2:
                return numeric_cols[0], numeric_cols[1]
            elif len(all_cols) >= 2:
                return all_cols[0], all_cols[1]
            else:
                raise ValueError("Table has fewer than 2 columns; cannot auto-detect x/y.")

        if not x_col:
            remaining = [c for c in numeric_cols if c != y_col] or [c for c in all_cols if c != y_col]
            x_col = remaining[0] if remaining else all_cols[0]

        if not y_col:
            remaining = [c for c in numeric_cols if c != x_col] or [c for c in all_cols if c != x_col]
            y_col = remaining[0] if remaining else all_cols[-1]

        return x_col, y_col

    @staticmethod
    def _q(col: str) -> str:
        """Quote a column name if it contains spaces or special characters."""
        if " " in col or "-" in col or "." in col:
            return f'"{col}"'
        return col

    def _render(self, table: str, x_col: str, y_col: str, chart_type: str = "line"):
        """Shared rendering logic."""

        sql = f"SELECT {self._q(x_col)}, {self._q(y_col)} FROM {table}"

        try:
            df = self.conn.execute(sql).fetchdf()
        except Exception as e:
            raise ValueError(f"Failed to query data for visualization: {e}\nSQL: {sql}")

        if df is None or df.empty:
            return {
                "analysis_type": "visualization",
                "chart_type": chart_type,
                "x": x_col,
                "y": y_col,
                "error": "No data returned for the selected columns.",
            }

        filename = f"{uuid.uuid4().hex}.png"
        filepath = os.path.join(self.output_dir, filename)

        plt.figure(figsize=(10, 6))

        if chart_type in ("line", "line_plot"):
            plt.plot(df.iloc[:, 0], df.iloc[:, 1], marker="o", markersize=4)
        elif chart_type in ("scatter", "scatter_plot"):
            plt.scatter(df.iloc[:, 0], df.iloc[:, 1], alpha=0.7, edgecolors="k", linewidths=0.5)
        elif chart_type in ("bar", "bar_chart"):
            plt.bar(df.iloc[:, 0], df.iloc[:, 1])
        elif chart_type in ("histogram", "hist"):
            plt.hist(df.iloc[:, 0], bins=20, edgecolor="black")
            plt.xlabel(x_col)
            plt.ylabel("Frequency")
            plt.title(f"Histogram of {x_col}")
            plt.tight_layout()
            plt.savefig(filepath, dpi=150)
            plt.close()
            return {
                "analysis_type": "visualization",
                "chart_type": chart_type,
                "x": x_col,
                "file_path": filepath,
            }
        else:
            # Default to scatter for unknown types
            plt.scatter(df.iloc[:, 0], df.iloc[:, 1], alpha=0.7)

        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.title(f"{y_col} vs {x_col}")
        plt.tight_layout()
        plt.savefig(filepath, dpi=150)
        plt.close()

        return {
            "analysis_type": "visualization",
            "chart_type": chart_type,
            "x": x_col,
            "y": y_col,
            "file_path": filepath,
        }