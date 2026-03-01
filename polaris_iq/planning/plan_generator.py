# polaris_iq/planning/plan_generator.py

import json
from polaris_iq.planning.plan_schema import QueryPlan


def generate_structured_plan(user_query: str, context: str, model) -> QueryPlan:

    prompt = f"""
You are PolarisIQ Query Compiler.

Convert the user request into STRICT JSON
matching this schema:

{QueryPlan.model_json_schema()}

Rules:
- Output JSON only
- Do not explain
- Use only provided columns

Context:
{context}

User Query:
{user_query}
"""

    raw_output = model.generate(prompt, temperature=0.0, max_tokens=800)

    parsed = json.loads(raw_output.strip())

    return QueryPlan(**parsed)
