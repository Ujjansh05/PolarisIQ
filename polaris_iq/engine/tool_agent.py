# engine/tool_agent.py

import json


class ToolAgent:
    MAX_TOOL_STEPS = 5

    def __init__(self, model, tool_executor):
        self.model = model
        self.tool_executor = tool_executor

    def run(self, user_query: str, context: str):

        history = []
        step_count = 0

        while step_count < self.MAX_TOOL_STEPS:
            prompt = self._build_prompt(user_query, context, history)

            response = self.model.generate(prompt, temperature=0.0)

            call = self._parse_tool_call(response)

            # If LLM says we're done
            if call["tool"] == "final_answer":
                return call["arguments"]["text"]

            # 🔥 THIS IS WHERE IT GOES
            result = self.tool_executor.execute(call["tool"], call["arguments"])

            history.append(
                {"tool": call["tool"], "arguments": call["arguments"], "result": result}
            )

            step_count += 1

        raise RuntimeError("ToolAgent exceeded maximum tool steps")

    def _build_prompt(self, user_query, context, history):
        return f"""
You are PolarisIQ Tool Agent.

Available tools: generate_plot, linear_regression, aggregation, etc.

User Query:
{user_query}

Context:
{context}

Previous Tool Calls:
{history}

Return JSON:
{{
  "tool": "...",
  "arguments": {{...}}
}}
"""

    def _parse_tool_call(self, response: str):
        return json.loads(response.strip())
