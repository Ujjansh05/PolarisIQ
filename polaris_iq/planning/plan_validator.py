# planning/plan_validator.py

from polaris_iq.core.exceptions import PlanValidationError


# Keys in parameters that are expected to contain column name references.
# All other keys (e.g. "sql", "aggregate", "function", "type") are skipped.
_COLUMN_KEYS = {
    "columns", "column", "group_by", "independent", "dependent",
    "column_x", "column_y", "target", "features",
}


def validate_plan(conn, plan, table_name: str):

    existing_columns = [
        row[0]
        for row in conn.execute(f"""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = '{table_name}'
        """).fetchall()
    ]

    if not existing_columns:
        raise PlanValidationError(
            f"Table '{table_name}' not found or has no columns."
        )

    column_lookup = {c.lower(): c for c in existing_columns}

    # Validate columns referenced in statistics
    if plan.statistics and plan.statistics.parameters:
        _validate_column_refs(plan.statistics.parameters, existing_columns, column_lookup)

    # Validate columns referenced in prediction
    if plan.prediction and plan.prediction.parameters:
        _validate_column_refs(plan.prediction.parameters, existing_columns, column_lookup)

    return True


def _resolve_column_name(value: str, existing_columns: list, column_lookup: dict) -> str | None:
    if value in existing_columns:
        return value
    if value == "*":
        return value
    return column_lookup.get(value.lower())


def _validate_column_refs(params: dict, existing_columns: list, column_lookup: dict):
    """Validate only known column-reference keys in a parameters dict."""

    for key, value in params.items():
        if key not in _COLUMN_KEYS:
            continue

        if value is None:
            continue

        if isinstance(value, list):
            for idx, col in enumerate(value):
                if isinstance(col, str) and col not in existing_columns:
                    resolved = _resolve_column_name(col, existing_columns, column_lookup)
                    if not resolved:
                        raise PlanValidationError(f"Invalid column: {col}")
                    value[idx] = resolved

        elif isinstance(value, str):
            if value not in existing_columns:
                resolved = _resolve_column_name(value, existing_columns, column_lookup)
                if not resolved:
                    raise PlanValidationError(f"Invalid column: {value}")
                params[key] = resolved
