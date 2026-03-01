# polaris_iq/planning/plan_generator.py

import ast
import json
import re
from polaris_iq.planning.plan_schema import QueryPlan


def _extract_json(text: str) -> str:
    """Extract JSON from LLM output, handling markdown fences and stray text."""

    text = text.strip()

    # 1. Try to extract content from markdown code fences: ```json ... ``` or ``` ... ```
    fence_match = re.search(r"```(?:json|JSON)?\s*\n?(.*?)\n?\s*```", text, re.DOTALL)
    if fence_match:
        return fence_match.group(1).strip()

    # 2. Fall back: extract the outermost { ... } or [ ... ] block
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
        # LLM may output Python-style dicts with single quotes or None/True/False
        try:
            result = ast.literal_eval(text)
            if isinstance(result, dict):
                return result
        except (ValueError, SyntaxError):
            pass
        # Re-raise the original JSON error for a clear message
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
- For regression_analysis, use the "prediction" field with "type": "linear_regression" and "parameters" containing "independent" (list of column names) and "dependent" (single column name).

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
