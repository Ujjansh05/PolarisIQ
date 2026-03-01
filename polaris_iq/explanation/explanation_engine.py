# explanation/explanation_engine.py


class ExplanationEngine:
    def generate(self, result: dict, explanation_level: str, model) -> str:

        prompt = f"""
You are PolarisIQ Explanation Engine.

Explain the following structured analytical result.
Do not invent numbers.
Do not modify values.
Be concise and precise.

Explanation level: {explanation_level}

Result:
{result}
"""

        return model.generate(prompt, temperature=0.2, max_tokens=600)
