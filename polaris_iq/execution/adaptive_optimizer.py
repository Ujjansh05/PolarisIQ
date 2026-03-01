class AdaptiveOptimizer:
    def __init__(self, conn):
        self.conn = conn

    def get_engine_performance(self, intent: str):

        result = self.conn.execute(
            """
        SELECT engine, AVG(execution_time)
        FROM polaris_execution_log
        WHERE intent = ?
        GROUP BY engine
        """,
            [intent],
        ).fetchall()

        return {row[0]: row[1] for row in result}

    def choose_best_engine(self, intent: str, fallback_engine: str):

        perf = self.get_engine_performance(intent)

        if not perf:
            return fallback_engine

        return min(perf, key=perf.get)
