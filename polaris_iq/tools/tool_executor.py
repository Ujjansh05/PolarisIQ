class ToolExecutor:
    def __init__(self, registry):
        self.registry = registry

    def execute(self, tool_name: str, args: dict):

        tool = self.registry.get(tool_name)

        if not tool:
            raise ValueError(f"Unknown tool: {tool_name}")

        handler = tool["handler"]

        return handler(**args)
