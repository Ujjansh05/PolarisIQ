# execution/sklearn_executor.py

from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from polaris_iq.core.exceptions import ExecutionError


class SklearnExecutor:
    def __init__(self, conn):
        self.conn = conn

    def execute(self, plan: dict):

        intent = plan["intent"]

        if intent == "regression_analysis":
            table = plan["data_scope"]["tables"][0]

            # Parameters may be in "prediction" or "statistics" depending on LLM output
            params = None
            if plan.get("prediction") and plan["prediction"].get("parameters"):
                params = plan["prediction"]["parameters"]
            elif plan.get("statistics") and plan["statistics"].get("parameters"):
                params = plan["statistics"]["parameters"]

            if not params or "independent" not in params or "dependent" not in params:
                raise ExecutionError(
                    "Regression plan is missing required 'independent'/'dependent' parameters."
                )

            df = self.conn.execute(f"SELECT * FROM {table}").fetchdf()

            independent = params["independent"]
            dependent = params["dependent"]

            # Normalize to list for independent variables
            if isinstance(independent, str):
                independent = [independent]

            X = df[independent]
            y = df[dependent]

            model = LinearRegression()
            model.fit(X, y)

            predictions = model.predict(X)
            r2 = r2_score(y, predictions)

            return {
                "analysis_type": "linear_regression",
                "r_squared": float(r2),
                "coefficients": dict(zip(independent, model.coef_)),
            }

        raise ExecutionError(f"Sklearn does not support intent: {intent}")
