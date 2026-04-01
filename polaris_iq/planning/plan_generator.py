# polaris_iq/planning/plan_generator.py

import ast
import json
import re
from polaris_iq.planning.plan_schema import QueryPlan


def _extract_json(text: str) -> str:
    """Extract JSON from LLM output, handling markdown fences and stray text."""

    text = text.strip()

    # 1. Try to extract content from markdown code fences
    fence_match = re.search(r"```(?:json|JSON)?\s*\n?(.*?)\n?\s*```", text, re.DOTALL)
    if fence_match:
        return fence_match.group(1).strip()

    # 2. Fall back: extract the outermost { ... } block
    start = text.find("{")
    if start != -1:
        end = text.rfind("}")
        if end != -1 and end > start:
            return text[start : end + 1]

    # 3. Nothing found — return as-is and let json.loads raise a clear error
    return text


def _parse_json_flexible(text: str) -> dict:
    """Parse JSON string, falling back to ast.literal_eval for single-quoted output."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        try:
            result = ast.literal_eval(text)
            if isinstance(result, dict):
                return result
        except (ValueError, SyntaxError):
            pass
        raise


def generate_structured_plan(user_query: str, context: str, model) -> QueryPlan:

    prompt = f"""
You are a strict JSON compiler.

Output ONLY valid JSON.
Do NOT include explanation.
Do NOT include markdown.
Do NOT include backticks.

The JSON must strictly match this schema:
{QueryPlan.model_json_schema()}

IMPORTANT CONSTRAINTS:
- "intent" MUST be one of: "aggregation", "correlation_analysis", "regression_analysis", "classification", "hypothesis_test", "feature_engineering", "visualization"
- "execution_engine" MUST be one of: "duckdb", "python_sklearn", "polars", "visualization"
- "explanation_level" MUST be one of: "brief", "detailed", "none"
- For aggregation, use the "statistics" field with "type" and "parameters". Parameters MUST contain "columns" (list of column names to aggregate), and optionally "group_by" (list of column names to group by) and "aggregate" (the function name, e.g. "AVG", "SUM", "COUNT", "MIN", "MAX"). You may also provide "sql" with a ready-to-run DuckDB SQL query.
- For correlation_analysis, use "statistics" with "parameters" containing "columns" (a list of 2 column names).
- For regression_analysis, use the "prediction" field with "type": "linear_regression" and "parameters" containing "independent" (list of column names) and "dependent" (single column name).
- For visualization, set "intent" to "visualization" and "execution_engine" to "visualization". Use the "statistics" field with "parameters" containing "x" (column name for x-axis), "y" (column name for y-axis), and "chart_type" (one of: "scatter", "line", "bar", "histogram", "pie", "custom"). Pick the most relevant numeric columns from the dataset for x and y. If the user asks for a very complex or highly customized chart (e.g. 3D, violin, heatmap, clustered), set "chart_type": "custom" and provide a "custom_code" parameter containing a raw Python script. The script will be executed with access to `df` (pandas DataFrame of the table) and `filepath` (string path to save the plot). The script MUST end with `plt.savefig(filepath)` to save the image. Do NOT include markdown blocks in the `custom_code` string itself, just raw python.

Example for aggregation (average salary by education level):
{{"intent":"aggregation","data_scope":{{"tables":["dummy_dataset"]}},"statistics":{{"type":["avg"],"parameters":{{"columns":["numeric_column_A"],"group_by":["category_column_B"],"aggregate":"AVG"}}}},"execution_engine":"duckdb","explanation_level":"brief"}}

Example for simple visualization (scatter plot):
{{"intent":"visualization","data_scope":{{"tables":["dummy_dataset"]}},"statistics":{{"type":["scatter"],"parameters":{{"x":"numeric_column_X","y":"numeric_column_Y","chart_type":"scatter"}}}},"execution_engine":"visualization","explanation_level":"brief"}}

Example for custom visualization (custom python code):
{{"intent":"visualization","data_scope":{{"tables":["dummy_dataset"]}},"statistics":{{"type":["custom"],"parameters":{{"chart_type":"custom","custom_code":"import seaborn as sns\\nimport matplotlib.pyplot as plt\\n\\nsns.violinplot(data=df, x='col_x', y='col_y')\\nplt.title('Custom Violin')\\nplt.savefig(filepath)\\nplt.close()"}}}},"execution_engine":"visualization","explanation_level":"brief"}}

Example for regression:
{{"intent":"regression_analysis","data_scope":{{"tables":["my_table"]}},"prediction":{{"type":"linear_regression","parameters":{{"independent":["col_x"],"dependent":"col_y"}}}},"execution_engine":"python_sklearn","explanation_level":"brief"}}

Context:
{context}

User Query:
{user_query}

Return JSON only.
"""

    raw_output = model.generate(prompt, temperature=0.0, max_tokens=800)

    if not raw_output or not raw_output.strip():
        raise ValueError("LLM returned empty output")

    cleaned = _extract_json(raw_output)

    parsed = _parse_json_flexible(cleaned)
    return QueryPlan(**parsed)
