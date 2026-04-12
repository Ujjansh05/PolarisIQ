# execution/duckdb_executor.py

import re

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
            try:
                return self._run_query(sql)
            except ExecutionError as e:
                # Fall back when LLM SQL references non-existent columns.
                if not self._is_missing_column_error(e):
                    raise

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

        if not columns and not group_by:
            return None

        agg_func = self._normalize_aggregate(aggregate)
        table_cols = self._get_table_columns(table)
        resolved_group_by, _ = self._resolve_columns(group_by or [], table_cols)
        resolved_columns, _ = self._resolve_columns(columns or [], table_cols)

        wildcard_requested = any(
            isinstance(c, str) and c.strip() == "*"
            for c in (columns or [])
        )

        select_parts = []
        if resolved_group_by:
            select_parts.extend([self._q(g) for g in resolved_group_by])

        # COUNT(*) is a common LLM fallback for "distribution"/"how many" style requests.
        if wildcard_requested and agg_func == "COUNT":
            select_parts.append("COUNT(*) AS count_all")

        for col in resolved_columns:
            safe = self._safe_alias(col)
            select_parts.append(f"{agg_func}({self._q(col)}) AS {agg_func.lower()}_{safe}")

        # If only group_by survived after column cleanup, default to counts per group.
        if resolved_group_by and len(select_parts) == len(resolved_group_by):
            select_parts.append("COUNT(*) AS count_all")

        # Nothing usable remains from the LLM plan; let caller try default summary.
        if not select_parts or (
            not resolved_columns and not wildcard_requested and not resolved_group_by
        ):
            return None

        sql = f"SELECT {', '.join(select_parts)} FROM {table}"

        if resolved_group_by:
            group_clause = ", ".join(self._q(g) for g in resolved_group_by)
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
                    safe = self._safe_alias(col)
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
        if isinstance(columns, str):
            columns = [columns]
        tables = (plan.get("data_scope") or {}).get("tables") or []

        if not tables:
            raise ExecutionError("No table specified in the plan.")

        table = tables[0]
        table_cols = self._get_table_columns(table)
        resolved_cols, _ = self._resolve_columns(columns, table_cols)

        # If columns are not specified or less than 2, return top precomputed correlations
        if len(resolved_cols) < 2:
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

        col_x, col_y = resolved_cols[0], resolved_cols[1]

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
        """Quote a column name when it is not a simple SQL identifier."""
        if not col:
            return col
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", col):
            return col
        escaped = col.replace('"', '""')
        return f'"{escaped}"'

    @staticmethod
    def _safe_alias(col: str) -> str:
        safe = re.sub(r"[^A-Za-z0-9_]+", "_", col).strip("_")
        return safe or "col"

    @staticmethod
    def _normalize_aggregate(aggregate) -> str:
        if not isinstance(aggregate, str):
            return "AVG"
        agg = aggregate.strip().upper()
        allowed = {
            "AVG",
            "SUM",
            "COUNT",
            "MIN",
            "MAX",
            "MEDIAN",
            "STDDEV",
            "STDDEV_SAMP",
            "STDDEV_POP",
            "VAR_SAMP",
            "VAR_POP",
        }
        return agg if agg in allowed else "AVG"

    def _get_table_columns(self, table: str) -> list[str]:
        try:
            cols = self.conn.execute(f"DESCRIBE {table}").fetchall()
            return [c[0] for c in cols]
        except Exception:
            return []

    @staticmethod
    def _column_lookup(columns: list[str]) -> dict[str, str]:
        lookup = {}
        for col in columns:
            # Exact
            lookup.setdefault(col, col)
            # Case-insensitive
            lookup.setdefault(col.lower(), col)
            # Compact form (e.g., Years Experience -> yearsexperience)
            compact = re.sub(r"[^a-z0-9]+", "", col.lower())
            if compact:
                lookup.setdefault(compact, col)
        return lookup

    def _resolve_column_name(self, col: str, lookup: dict[str, str]) -> str | None:
        if not isinstance(col, str):
            return None
        candidate = col.strip().strip('`').strip('"').strip("'")
        if not candidate:
            return None
        if candidate in lookup:
            return lookup[candidate]
        lowered = candidate.lower()
        if lowered in lookup:
            return lookup[lowered]
        compact = re.sub(r"[^a-z0-9]+", "", lowered)
        return lookup.get(compact)

    def _resolve_columns(self, requested_cols: list, table_cols: list[str]) -> tuple[list[str], list[str]]:
        if not requested_cols or not table_cols:
            return [], requested_cols or []

        lookup = self._column_lookup(table_cols)
        resolved = []
        missing = []
        seen = set()

        for col in requested_cols:
            matched = self._resolve_column_name(col, lookup)
            if not matched:
                missing.append(col)
                continue

            key = matched.lower()
            if key in seen:
                continue
            seen.add(key)
            resolved.append(matched)

        return resolved, missing

    @staticmethod
    def _is_missing_column_error(err: Exception) -> bool:
        text = str(err)
        lowered = text.lower()
        return "referenced column" in lowered or (
            "binder error" in lowered and "not found" in lowered
        )

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
