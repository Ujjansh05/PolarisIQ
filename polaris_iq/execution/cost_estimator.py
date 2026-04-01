# execution/cost_estimator.py


class CostEstimator:
    def __init__(self, conn):
        self.conn = conn

    def estimate(self, plan, table_name: str) -> dict:

        try:
            result = self.conn.execute(
                f"SELECT COUNT(*) FROM {table_name}"
            ).fetchone()
            row_count = result[0] if result else 0
        except Exception:
            row_count = 0

        try:
            result = self.conn.execute(
                f"""
                SELECT COUNT(*)
                FROM information_schema.columns
                WHERE table_name = '{table_name}'
                """
            ).fetchone()
            col_count = result[0] if result else 0
        except Exception:
            col_count = 0

        return {
            "row_count": row_count,
            "column_count": col_count,
            "intent": plan.intent,
        }
