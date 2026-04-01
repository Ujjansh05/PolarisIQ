# engine/tool_agent.py

import ast
import json
import re


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
            call = self._normalize_tool_call(call)

            # If LLM says we're done
            if call["tool"] == "final_answer":
                return call["arguments"].get("text", str(call["arguments"]))

            # Execute the tool
            result = self.tool_executor.execute(call["tool"], call["arguments"])

            # For single-action tools (generate_plot etc.), return immediately
            # since the tool execution IS the final result
            return result

        raise RuntimeError("ToolAgent exceeded maximum tool steps")

    def _normalize_tool_call(self, call: dict) -> dict:
        """Normalize different LLM output formats into {"tool": ..., "arguments": ...}."""

        # Already in correct format
        if "tool" in call and "arguments" in call:
            return call

        # Handle alternative key names
        tool = call.get("tool") or call.get("name") or call.get("function")
        args = call.get("arguments") or call.get("params") or call.get("parameters") or call.get("args")

        if tool and args:
            return {"tool": tool, "arguments": args}

        # If no "tool" key, check if it looks like direct tool arguments (x, y present)
        if "x" in call and "y" in call:
            return {"tool": "generate_plot", "arguments": call}

        # If the call contains a "text" or "answer" field, treat as final_answer
        if "text" in call or "answer" in call:
            text = call.get("text") or call.get("answer", "")
            return {"tool": "final_answer", "arguments": {"text": text}}

        # Last resort: treat entire output as final answer
        return {"tool": "final_answer", "arguments": {"text": str(call)}}

    def _build_prompt(self, user_query, context, history):
        history_str = json.dumps(history, indent=2, default=str) if history else "None"

        return f"""You are PolarisIQ Tool Agent. You must call tools to answer the user's query.
Use the column names from the Context below. Do NOT use placeholder names.

Available tools:

1. generate_plot
   Parameters: x (string, column name), y (string, column name), chart_type (string: "line", "scatter", or "bar"), table (string, table name)
   Description: Generates a plot from database columns.

2. correlation_analysis
   Parameters: table (string, table name)
   Description: Gets all precomputed column correlations for the dataset.

3. final_answer
   Parameters: text (string, your final answer text)
   Description: Use this when you have completed the task and want to return the result.

{context}

User Query: {user_query}

Previous Tool Calls:
{history_str}

Respond with ONLY a single valid JSON object. Example:
{{"tool": "generate_plot", "arguments": {{"x": "numeric_column_X", "y": "numeric_column_Y", "chart_type": "line", "table": "dummy_table"}}}}
"""

    def _parse_tool_call(self, response: str) -> dict:
        text = response.strip()

        # Try to extract JSON from markdown fences
        fence_match = re.search(r"```(?:json|JSON)?\s*\n?(.*?)\n?\s*```", text, re.DOTALL)
        if fence_match:
            text = fence_match.group(1).strip()

        # Find the first { in the text
        start = text.find("{")
        if start != -1:
            text = text[start:]

        # Use raw_decode to parse only the first JSON object (ignores trailing text)
        decoder = json.JSONDecoder()
        try:
            result, _ = decoder.raw_decode(text)
            if isinstance(result, dict):
                return result
        except json.JSONDecodeError:
            pass

        # Fallback: try ast.literal_eval on the outermost { ... }
        end = text.rfind("}")
        if end != -1:
            candidate = text[: end + 1]
            try:
                result = ast.literal_eval(candidate)
                if isinstance(result, dict):
                    return result
            except (ValueError, SyntaxError):
                pass

        raise json.JSONDecodeError("Could not parse tool call from LLM output", text, 0)
