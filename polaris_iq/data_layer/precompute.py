# data_layer/precompute.py
from pathlib import Path
import duckdb
import polars as pl


# ============================================================
# FORMAT LOADERS
# ============================================================


def load_csv_tsv(file_path: str) -> pl.DataFrame:
    return pl.read_csv(file_path)


def load_parquet(conn: duckdb.DuckDBPyConnection, file_path: str, table_name: str):
    conn.execute(f"""
        CREATE OR REPLACE TABLE {table_name} AS
        SELECT * FROM read_parquet('{file_path}')
    """)


def load_json_ndjson(conn: duckdb.DuckDBPyConnection, file_path: str, table_name: str):
    conn.execute(f"""
        CREATE OR REPLACE TABLE {table_name} AS
        SELECT * FROM read_json_auto('{file_path}')
    """)


def load_excel(file_path: str) -> pl.DataFrame:
    return pl.read_excel(file_path)


def load_existing_duckdb(conn: duckdb.DuckDBPyConnection, file_path: str):
    # Attach existing DuckDB file
    conn.execute(f"ATTACH '{file_path}' AS source_db")
    return "source_db"


# ============================================================
# PERSISTENCE LAYER
# ============================================================


def persist_polars_to_duckdb(
    conn: duckdb.DuckDBPyConnection, df: pl.DataFrame, table_name: str
):
    arrow_table = df.to_arrow()
    conn.register("temp_arrow_table", arrow_table)

    conn.execute(f"""
        CREATE OR REPLACE TABLE {table_name} AS
        SELECT * FROM temp_arrow_table
    """)

    conn.unregister("temp_arrow_table")


# ============================================================
# PROFILING LAYER
# ============================================================


def run_schema_profiling(conn: duckdb.DuckDBPyConnection, table_name: str):
    cols = [r[0] for r in conn.execute(f"DESCRIBE {table_name}").fetchall()]
    unpivot_cols = ", ".join([f'"{c}"' for c in cols])
    select_cast = ", ".join([f'"{c}"::VARCHAR AS "{c}"' for c in cols])

    try:
        conn.execute("SELECT table_name FROM polaris_metadata LIMIT 1")
    except Exception:
        conn.execute("DROP TABLE IF EXISTS polaris_metadata")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS polaris_metadata (
            table_name VARCHAR,
            column_name VARCHAR,
            data_type VARCHAR,
            null_ratio DOUBLE
        )
    """)
    conn.execute(f"DELETE FROM polaris_metadata WHERE table_name = '{table_name}'")

    conn.execute(f"""
        INSERT INTO polaris_metadata
        SELECT
            '{table_name}',
            u.column_name,
            i.data_type,
            COUNT(*) FILTER (WHERE u.value IS NULL) * 1.0 / COUNT(*) AS null_ratio
        FROM (
            SELECT {select_cast} FROM {table_name}
        )
        UNPIVOT(value FOR column_name IN ({unpivot_cols})) u
        JOIN information_schema.columns i
            ON i.column_name = u.column_name
            AND i.table_name = '{table_name}'
        GROUP BY u.column_name, i.data_type
    """)


def run_statistical_profiling(conn: duckdb.DuckDBPyConnection, table_name: str):
    cols = conn.execute(f"DESCRIBE {table_name}").fetchall()
    numeric_cols = [
        c[0] for c in cols 
        if any(t in c[1].upper() for t in ["INT", "FLOAT", "DOUBLE", "DECIMAL", "BIGINT", "NUMERIC"])
    ]
    if not numeric_cols:
        conn.execute("CREATE OR REPLACE TABLE polaris_statistics(column_name VARCHAR, mean DOUBLE, std DOUBLE, min DOUBLE, max DOUBLE)")
        return
        
    unpivot_cols = ", ".join([f'"{c}"' for c in numeric_cols])
    select_cast = ", ".join([f'"{c}"::DOUBLE AS "{c}"' for c in numeric_cols])

    try:
        conn.execute("SELECT table_name FROM polaris_statistics LIMIT 1")
    except Exception:
        conn.execute("DROP TABLE IF EXISTS polaris_statistics")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS polaris_statistics (
            table_name VARCHAR,
            column_name VARCHAR,
            mean DOUBLE,
            std DOUBLE,
            min DOUBLE,
            max DOUBLE
        )
    """)
    conn.execute(f"DELETE FROM polaris_statistics WHERE table_name = '{table_name}'")

    conn.execute(f"""
        INSERT INTO polaris_statistics
        SELECT
            '{table_name}',
            column_name,
            avg(value) AS mean,
            stddev(value) AS std,
            min(value) AS min,
            max(value) AS max
        FROM (
            SELECT {select_cast} FROM {table_name}
        )
        UNPIVOT(value FOR column_name IN ({unpivot_cols}))
        GROUP BY column_name
    """)


def run_correlation_profiling(conn: duckdb.DuckDBPyConnection, table_name: str):
    # Simplified pairwise correlation generation
    numeric_cols = conn.execute(f"""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = '{table_name}'
        AND data_type IN ('INTEGER', 'DOUBLE')
    """).fetchall()

    numeric_cols = [col[0] for col in numeric_cols]

    try:
        conn.execute("SELECT table_name FROM polaris_correlations LIMIT 1")
    except Exception:
        conn.execute("DROP TABLE IF EXISTS polaris_correlations")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS polaris_correlations (
            table_name VARCHAR,
            column_x VARCHAR,
            column_y VARCHAR,
            correlation DOUBLE
        )
    """)
    conn.execute(f"DELETE FROM polaris_correlations WHERE table_name = '{table_name}'")

    for i in range(len(numeric_cols)):
        for j in range(i + 1, len(numeric_cols)):
            col_x = numeric_cols[i]
            col_y = numeric_cols[j]

            result = conn.execute(f"""
                SELECT corr("{col_x}", "{col_y}")
                FROM {table_name}
            """).fetchone()[0]

            conn.execute(
                """
                INSERT INTO polaris_correlations VALUES (?, ?, ?, ?)
            """,
                [table_name, col_x, col_y, result],
            )


# ============================================================
# MASTER PRECOMPUTATION FUNCTION
# ============================================================


def precompute(input_path: str, table_name: str, duckdb_path: str = "polaris.db"):
    """
    Precompute pipeline:
    1. Load data (format-specific)
    2. Persist into DuckDB
    3. Run profiling (schema + stats + correlations)
    """

    input_path = Path(input_path)
    ext = input_path.suffix.lower()

    conn = duckdb.connect(duckdb_path)

    print(f"Precomputing for {input_path.name}...")

    # ----------------------------
    # Load & Persist
    # ----------------------------

    if ext in [".csv", ".tsv"]:
        df = load_csv_tsv(str(input_path))
        persist_polars_to_duckdb(conn, df, table_name)

    elif ext == ".parquet":
        load_parquet(conn, str(input_path), table_name)

    elif ext in [".json", ".ndjson"]:
        load_json_ndjson(conn, str(input_path), table_name)

    elif ext in [".xlsx", ".xls"]:
        df = load_excel(str(input_path))
        persist_polars_to_duckdb(conn, df, table_name)

    elif ext == ".duckdb":
        print("Using existing DuckDB file directly.")
        conn.close()
        return

    else:
        raise ValueError(f"Unsupported file format: {ext}")

    # ----------------------------
    # Profiling Phase
    # ----------------------------

    print("Running schema profiling...")
    run_schema_profiling(conn, table_name)

    print("Running statistical profiling...")
    run_statistical_profiling(conn, table_name)

    print("Running correlation profiling...")
    run_correlation_profiling(conn, table_name)

    conn.close()

    print("Precomputation complete.")
