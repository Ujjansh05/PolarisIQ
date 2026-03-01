# engine/autonomous_engine.py

from polaris_iq.planning.context_builder import build_llm_context


class AutonomousEngine:
    def __init__(
        self, orchestrator, task_decomposer, self_critic, max_iterations: int = 3
    ):
        self.orchestrator = orchestrator
        self.task_decomposer = task_decomposer
        self.self_critic = self_critic
        self.max_iterations = max_iterations

    def execute(self, user_query: str, table_name: str):

        context = build_llm_context(self.orchestrator.conn, table_name)

        steps = self.task_decomposer.decompose(user_query, context)

        iteration = 0
        final_output = None

        while iteration < self.max_iterations:
            for step in steps:
                final_output = self.orchestrator.handle_query(step, table_name)

            needs_refinement = self.self_critic.evaluate(final_output)

            if not needs_refinement:
                break

            # Ask LLM to refine
            refinement_query = f"Refine this analysis: {final_output}"
            steps = self.task_decomposer.decompose(refinement_query, context)

            iteration += 1

        return final_output
