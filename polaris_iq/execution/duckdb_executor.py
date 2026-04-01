# execution/duckdb_executor.py

from polaris_iq.core.exceptions import ExecutionError


class DuckDBExecutor:
    def __init__(self, conn):
        self.conn = conn

    def execute(self, plan: dict):
        intent = plan.get("intent")

        if intent == "aggregation":
            return self._execute_aggregation(plan)

        if intent == "correlation_analysis":
            return self._execute_correlation(plan)

        raise ExecutionError(f"DuckDB does not support intent: {intent}")

    # ── Aggregation ──────────────────────────────────────────────

    def _execute_aggregation(self, plan: dict):
        stats = plan.get("statistics") or {}
        params = stats.get("parameters") or {}
        tables = (plan.get("data_scope") or {}).get("tables") or []

        if not tables:
            raise ExecutionError("No table specified in the plan.")

        table = tables[0]

        # Priority 1: use explicitly provided SQL from the LLM
        sql = params.get("sql")
        if sql and isinstance(sql, str) and sql.strip():
            return self._run_query(sql)

        # Priority 2: build SQL from semantic parameters (columns, group_by, aggregate)
        sql = self._build_aggregation_sql(params, table)
        if sql:
            return self._run_query(sql)

        # Priority 3: fall back to full numeric column summary
        sql = self._build_default_summary(table)
        return self._run_query(sql)

    def _build_aggregation_sql(self, params: dict, table: str):
        """Build aggregation SQL from semantic fields like columns, group_by, aggregate."""

        columns = params.get("columns") or params.get("column")
        group_by = params.get("group_by")
        aggregate = params.get("aggregate") or params.get("function") or "AVG"

        # Normalise to lists
        if isinstance(columns, str):
            columns = [columns]
        if isinstance(group_by, str):
            group_by = [group_by]

        if not columns:
            return None

        agg_func = aggregate.upper() if isinstance(aggregate, str) else "AVG"

        select_parts = []
        if group_by:
            select_parts.extend([self._q(g) for g in group_by])

        for col in columns:
            safe = col.replace(" ", "_")
            select_parts.append(f"{agg_func}({self._q(col)}) AS {agg_func.lower()}_{safe}")

        sql = f"SELECT {', '.join(select_parts)} FROM {table}"

        if group_by:
            group_clause = ", ".join(self._q(g) for g in group_by)
            sql += f" GROUP BY {group_clause}"
            sql += f" ORDER BY {group_clause}"

        return sql

    def _build_default_summary(self, table: str):
        """Build a default summary SQL for all numeric columns."""
        try:
            cols = self.conn.execute(f"DESCRIBE {table}").fetchall()
            numeric_cols = [
                c[0]
                for c in cols
                if any(
                    t in c[1].upper()
                    for t in ["INT", "FLOAT", "DOUBLE", "DECIMAL", "BIGINT", "NUMERIC"]
                )
            ]
            if numeric_cols:
                agg_parts = []
                for col in numeric_cols:
                    qc = self._q(col)
                    safe = col.replace(" ", "_")
                    agg_parts.append(f"AVG({qc}) AS avg_{safe}")
                    agg_parts.append(f"MIN({qc}) AS min_{safe}")
                    agg_parts.append(f"MAX({qc}) AS max_{safe}")
                return f"SELECT {', '.join(agg_parts)} FROM {table}"
        except Exception:
            pass

        return f"SELECT COUNT(*) AS row_count FROM {table}"

    # ── Correlation ──────────────────────────────────────────────

    def _execute_correlation(self, plan: dict):
        stats = plan.get("statistics") or {}
        params = stats.get("parameters") or {}
        columns = params.get("columns") or []
        tables = (plan.get("data_scope") or {}).get("tables") or []

        if not tables:
            raise ExecutionError("No table specified in the plan.")

        table = tables[0]

        # If columns are not specified or less than 2, return top precomputed correlations
        if len(columns) < 2:
            try:
                # Query precomputed correlations
                result = self.conn.execute(
                    f"SELECT column_x, column_y, correlation FROM polaris_correlations "
                    f"WHERE correlation IS NOT NULL AND table_name = '{table}' "
                    f"ORDER BY abs(correlation) DESC LIMIT 10"
                ).fetchall()
                
                correlations = [{"col_x": r[0], "col_y": r[1], "corr": round(r[2], 4)} for r in result]
                return {
                    "analysis_type": "correlation_summary",
                    "top_correlations": correlations
                }
            except Exception:
                raise ExecutionError(
                    "Correlation analysis requires at least 2 columns "
                    "in 'statistics.parameters.columns', and fallback precomputed correlations failed."
                )

        col_x, col_y = columns[0], columns[1]

        try:
            result = self.conn.execute(
                f"SELECT corr({self._q(col_x)}, {self._q(col_y)}) FROM {table}"
            ).fetchone()

            corr_value = result[0] if result is not None else None
        except Exception as e:
            raise ExecutionError(f"Correlation query failed: {e}")

        return {
            "analysis_type": "correlation",
            "correlation": float(corr_value) if corr_value is not None else None,
        }


    # ── Helpers ──────────────────────────────────────────────────

    @staticmethod
    def _q(col: str) -> str:
        """Quote a column name if it contains spaces or special characters."""
        if " " in col or "-" in col or "." in col:
            return f'"{col}"'
        return col

    def _run_query(self, sql: str) -> dict:
        """Execute SQL and return results as a dict with null-safety."""
        try:
            result = self.conn.execute(sql)
            if result is None:
                return {"result": "Query executed but returned no result object.", "sql": sql}

            df = result.fetchdf()
            if df is None or df.empty:
                return {"result": "Query returned no data.", "sql": sql}

            return df.to_dict()
        except Exception as e:
            raise ExecutionError(f"DuckDB query failed: {e}\nSQL: {sql}")
