# planning/task_decomposer.py


class TaskDecomposer:
    def __init__(self, model):
        self.model = model

    def decompose(self, user_query: str, context: str) -> list:

        prompt = f"""
You are PolarisIQ Autonomous Planner.

Break the user request into ordered atomic analytical steps.
Each step must be executable independently.

Return JSON list only.

User Query:
{user_query}
"""

        response = self.model.generate(prompt, temperature=0.0)

        import json

        return json.loads(response)
