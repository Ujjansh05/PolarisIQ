# explanation/explanation_engine.py


class ExplanationEngine:

    _SYSTEM_PROMPT = (
        "You are PolarisIQ Explanation Engine. "
        "Your job is to DIRECTLY ANSWER the user's question using the analytical results provided. "
        "Do not just describe the results generically — interpret them to answer the specific question asked. "
        "If the results contain regression coefficients and the user asks about a specific value, "
        "compute the answer using the coefficients and dataset statistics. "
        "When explaining mathematical formulas or equations, you MUST wrap them in double dollar signs `$$ ... $$` for block equations and single dollar signs `$ ... $` for inline math. "
        "CRITICAL: Never use the `$` symbol for currency (e.g., do not write $1000). Always spell it out or use `USD` (e.g., 1000 USD) to ensure the math renderer only parses actual equations. "
        "Do not output JSON. Do not invent numbers. Do not include file paths in your answer."
    )

    def generate(
        self,
        result: dict,
        explanation_level: str,
        model,
        user_query: str = "",
        context: str = "",
    ) -> str:

        prompt = f"""
The user asked: "{user_query}"

Using the analytical result below, DIRECTLY ANSWER the user's question.
Do not just describe the result — compute and state the specific answer.
If the result contains regression coefficients (intercept, slope) and the user asks
"at what value of X does Y equal Z", solve the equation and give the number.
Use the dataset statistics provided to look up values like mean, min, max.
Do not mention file paths or internal storage details.
CRITICAL: DO NOT use the `$` symbol for money or currency. Use `USD`. 
HOWEVER, you MUST use `$$ ... $$` to wrap block mathematical formulas, and `$ ... $` for inline math. Do NOT use `\\[` and `\\]`.

Explanation level: {explanation_level}

Dataset Context:
{context}

Analytical Result:
{result}

Answer the user's question directly and concisely:
"""

        return model.generate(
            prompt,
            temperature=0.2,
            max_tokens=600,
            system_prompt=self._SYSTEM_PROMPT,
        )
