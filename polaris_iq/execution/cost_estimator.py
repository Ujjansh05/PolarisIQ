# execution/cost_estimator.py


class CostEstimator:
    def __init__(self, conn):
        self.conn = conn

    def estimate(self, plan, table_name: str) -> dict:

        row_count = self.conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[
            0
        ]

        col_count = self.conn.execute(
            f"""
            SELECT COUNT(*)
            FROM information_schema.columns
            WHERE table_name = '{table_name}'
            """
        ).fetchone()[0]

        return {
            "row_count": row_count,
            "column_count": col_count,
            "intent": plan.intent,
        }
