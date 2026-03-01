class WorkflowEngine:
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator

    def execute_workflow(self, steps: list, table_name: str):

        intermediate_result = None

        for step in steps:
            intermediate_result = self.orchestrator.handle_query(step, table_name)

        return intermediate_result
