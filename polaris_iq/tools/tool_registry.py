# tools/tool_registry.py


class ToolRegistry:
    def __init__(self):
        self.tools = {}

    def register(self, name: str, handler, schema: dict):
        self.tools[name] = {"handler": handler, "schema": schema}

    def get(self, name: str):
        return self.tools.get(name)

    def list_tools(self):
        return list(self.tools.keys())


# ------------------------------------------------
# Tool Schemas
# ------------------------------------------------

VISUALIZATION_SCHEMA = {
    "name": "generate_plot",
    "parameters": {
        "type": "object",
        "properties": {
            "x": {"type": "string"},
            "y": {"type": "string"},
            "chart_type": {"type": "string", "enum": ["line", "scatter", "bar"]},
            "table": {"type": "string"},
        },
        "required": ["x", "y", "table"],
    },
}

CORRELATION_SCHEMA = {
    "name": "correlation_analysis",
    "parameters": {
        "type": "object",
        "properties": {
            "table": {"type": "string"}
        },
        "required": []
    }
}
