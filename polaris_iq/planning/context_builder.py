# planning/context_builder.py

import duckdb


def build_llm_context(conn: duckdb.DuckDBPyConnection, table_name: str) -> str:

    try:
        metadata = conn.execute("""
            SELECT column_name, data_type, null_ratio
            FROM polaris_metadata
        """).fetchall()
    except Exception:
        metadata = []

    try:
        stats = conn.execute("""
            SELECT column_name, mean, std, min, max
            FROM polaris_statistics
        """).fetchall()
    except Exception:
        stats = []

    context = f"Dataset: {table_name}\n\nColumns:\n"

    if metadata:
        for col in metadata:
            null_ratio = round(col[2], 4) if col[2] is not None else 0
            context += f"- {col[0]} ({col[1]}), null_ratio={null_ratio}\n"
    else:
        # Fall back to DESCRIBE if polaris_metadata is missing
        try:
            cols = conn.execute(f"DESCRIBE {table_name}").fetchall()
            for col in cols:
                context += f"- {col[0]} ({col[1]})\n"
        except Exception:
            context += "- (no column info available)\n"

    context += "\nStatistics:\n"

    if stats:
        for s in stats:
            mean = round(s[1], 4) if s[1] is not None else "N/A"
            std = round(s[2], 4) if s[2] is not None else "N/A"
            smin = round(s[3], 4) if s[3] is not None else "N/A"
            smax = round(s[4], 4) if s[4] is not None else "N/A"
            context += f"- {s[0]}: mean={mean}, std={std}, min={smin}, max={smax}\n"
    else:
        context += "- (no statistics available)\n"

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
