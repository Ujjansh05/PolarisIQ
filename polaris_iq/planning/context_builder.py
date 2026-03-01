# planning/context_builder.py

import duckdb


def build_llm_context(conn: duckdb.DuckDBPyConnection, table_name: str) -> str:
    metadata = conn.execute("""
        SELECT column_name, data_type, null_ratio
        FROM polaris_metadata
    """).fetchall()

    stats = conn.execute("""
        SELECT column_name, mean, std, min, max
        FROM polaris_statistics
    """).fetchall()

    context = f"Dataset: {table_name}\n\nColumns:\n"

    for col in metadata:
        context += f"- {col[0]} ({col[1]}), null_ratio={round(col[2], 4)}\n"

    context += "\nStatistics:\n"

    for s in stats:
        context += f"- {s[0]}: mean={s[1]}, std={s[2]}, min={s[3]}, max={s[4]}\n"

    context += """
Available Capabilities:
- aggregation
- correlation_analysis
- regression_analysis
- classification
- hypothesis_test
- feature_engineering
"""

    return context
