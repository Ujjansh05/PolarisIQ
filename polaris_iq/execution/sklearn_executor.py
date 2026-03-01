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
            params = plan["statistics"]["parameters"]

            df = self.conn.execute(f"SELECT * FROM {table}").fetchdf()

            X = df[params["independent"]]
            y = df[params["dependent"]]

            model = LinearRegression()
            model.fit(X, y)

            predictions = model.predict(X)
            r2 = r2_score(y, predictions)

            return {
                "analysis_type": "linear_regression",
                "r_squared": float(r2),
                "coefficients": dict(zip(params["independent"], model.coef_)),
            }

        raise ExecutionError(f"Sklearn does not support intent: {intent}")
