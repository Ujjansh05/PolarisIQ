# explanation/self_critic.py


class SelfCritic:
    """
    Evaluates whether an analytical result needs refinement.
    Used only in Autonomous Mode (Phase 6).
    """

    def __init__(self, model, threshold_confidence: float = 0.5):
        self.model = model
        self.threshold_confidence = threshold_confidence

    def evaluate(self, result: dict) -> bool:
        """
        Returns True if refinement is needed.
        Returns False if result is sufficient.
        """

        prompt = f"""
You are PolarisIQ Quality Evaluator.

Determine whether the following analytical result is sufficient
to fully answer the original query.

Return ONLY one word:
REFINE
or
SUFFICIENT

Result:
{result}
"""

        response = self.model.generate(prompt, temperature=0.0, max_tokens=10)

        response = response.strip().upper()

        if "REFINE" in response:
            return True

        return False
