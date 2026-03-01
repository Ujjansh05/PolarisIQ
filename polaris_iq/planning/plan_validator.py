# planning/plan_validator.py

from polaris_iq.core.exceptions import PlanValidationError


def validate_plan(conn, plan, table_name: str):

    existing_columns = [
        row[0]
        for row in conn.execute(f"""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = '{table_name}'
        """).fetchall()
    ]

    # Validate referenced columns
    if plan.statistics:
        params = plan.statistics.parameters
        for key in params:
            if isinstance(params[key], list):
                for col in params[key]:
                    if col not in existing_columns:
                        raise PlanValidationError(f"Invalid column: {col}")
            else:
                if params[key] not in existing_columns:
                    raise PlanValidationError(f"Invalid column: {params[key]}")

    return True
