import time


class ExecutionLogger:
    def __init__(self, conn):
        self.conn = conn

        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS polaris_execution_log (
            timestamp TIMESTAMP,
            intent VARCHAR,
            engine VARCHAR,
            row_count BIGINT,
            execution_time DOUBLE
        )
        """)

    def log(self, intent, engine, row_count, duration):
        self.conn.execute(
            """
        INSERT INTO polaris_execution_log
        VALUES (CURRENT_TIMESTAMP, ?, ?, ?, ?)
        """,
            [intent, engine, row_count, duration],
        )
