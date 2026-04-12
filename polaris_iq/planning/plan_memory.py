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
            plan_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Backward-compatible migration for existing DBs created before created_at existed.
        try:
            self.conn.execute("SELECT created_at FROM polaris_plan_memory LIMIT 1")
        except Exception:
            try:
                self.conn.execute("ALTER TABLE polaris_plan_memory ADD COLUMN created_at TIMESTAMP")
            except Exception:
                pass

    def _hash_query(self, query: str, table_name: str):
        key = f"{table_name}::{query}"
        return hashlib.sha256(key.encode()).hexdigest()

    def store(self, query: str, table_name: str, plan: dict):
        query_hash = self._hash_query(query, table_name)
        plan_json = json.dumps(plan)

        # Keep only one latest plan per query+table key.
        self.conn.execute(
            """
            DELETE FROM polaris_plan_memory
            WHERE query_hash = ?
            """,
            [query_hash],
        )

        try:
            self.conn.execute(
                """
                INSERT INTO polaris_plan_memory (query_hash, original_query, plan_json, created_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                """,
                [query_hash, query, plan_json],
            )
        except Exception:
            # Fallback for very old schemas if migration was not possible.
            self.conn.execute(
                """
                INSERT INTO polaris_plan_memory (query_hash, original_query, plan_json)
                VALUES (?, ?, ?)
                """,
                [query_hash, query, plan_json],
            )

    def retrieve(self, query: str, table_name: str):
        query_hash = self._hash_query(query, table_name)

        try:
            result = self.conn.execute(
                """
                SELECT plan_json
                FROM polaris_plan_memory
                WHERE query_hash = ?
                ORDER BY created_at DESC NULLS LAST
                LIMIT 1
                """,
                [query_hash],
            ).fetchone()
        except Exception:
            result = self.conn.execute(
                """
                SELECT plan_json
                FROM polaris_plan_memory
                WHERE query_hash = ?
                LIMIT 1
                """,
                [query_hash],
            ).fetchone()

        if result:
            return json.loads(result[0])

        return None

    def delete(self, query: str, table_name: str):
        query_hash = self._hash_query(query, table_name)
        self.conn.execute(
            """
            DELETE FROM polaris_plan_memory
            WHERE query_hash = ?
            """,
            [query_hash],
        )
