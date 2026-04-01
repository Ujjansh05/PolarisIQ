# planning/plan_memory.py

import hashlib
import json


class PlanMemory:
    def __init__(self, conn):
        self.conn = conn

        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS polaris_plan_memory (
            query_hash VARCHAR,
            original_query VARCHAR,
            plan_json TEXT
        )
        """)

    def _hash_query(self, query: str, table_name: str):
        key = f"{table_name}::{query}"
        return hashlib.sha256(key.encode()).hexdigest()

    def store(self, query: str, table_name: str, plan: dict):
        query_hash = self._hash_query(query, table_name)

        self.conn.execute(
            """
        INSERT INTO polaris_plan_memory VALUES (?, ?, ?)
        """,
            [query_hash, query, json.dumps(plan)],
        )

    def retrieve(self, query: str, table_name: str):
        query_hash = self._hash_query(query, table_name)

        result = self.conn.execute(
            """
        SELECT plan_json
        FROM polaris_plan_memory
        WHERE query_hash = ?
        """,
            [query_hash],
        ).fetchone()

        if result:
            return json.loads(result[0])

        return None
