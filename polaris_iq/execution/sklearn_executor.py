# execution/sklearn_executor.py

from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import r2_score, accuracy_score
from polaris_iq.core.exceptions import ExecutionError


class SklearnExecutor:
    def __init__(self, conn):
        self.conn = conn

    def execute(self, plan: dict):

        intent = plan.get("intent", "regression_analysis")

        if intent in ["regression_analysis", "classification"]:
            table = plan["data_scope"]["tables"][0]

            # Parameters may be in "prediction" or "statistics" depending on LLM output
            params = None
            if plan.get("prediction") and plan["prediction"].get("parameters"):
                params = plan["prediction"]["parameters"]
            elif plan.get("statistics") and plan["statistics"].get("parameters"):
                params = plan["statistics"]["parameters"]

            if not params or "independent" not in params or "dependent" not in params:
                 return {"analysis_type": intent, "error": "Plan is missing required 'independent'/'dependent' parameters."}

            try:
                df = self.conn.execute(f"SELECT * FROM {table}").fetchdf()
            except Exception as e:
                return {"analysis_type": intent, "error": f"Failed to fetch table '{table}': {e}"}

            independent = params["independent"]
            dependent = params["dependent"]

            # Normalize to list for independent variables
            if isinstance(independent, str):
                independent = [independent]
            
            # Deduplicate independent columns to prevent X[col] from returning a DataFrame
            independent = list(dict.fromkeys(independent))
            
            # Normalize to string for dependent variable
            if isinstance(dependent, list) and len(dependent) > 0:
                dependent = dependent[0]
            elif isinstance(dependent, list):
                return {"analysis_type": intent, "error": "Dependent parameter cannot be an empty list."}

            # Avoid Target Leakage & Duplicate Columns
            if dependent in independent:
                independent.remove(dependent)

            # Validate columns
            if dependent not in df.columns:
                return {"analysis_type": intent, "error": f"Dependent variable '{dependent}' does not exist in dataset."}

            actual_ind = [c for c in independent if c in df.columns]
            if not actual_ind:
                actual_ind = [c for c in df.select_dtypes(include=['number']).columns if c != dependent][:3]
                if not actual_ind:
                    return {"analysis_type": intent, "error": f"None of the requested independent variables exist, and no numeric fallbacks were found."}
            independent = actual_ind

            # Drop missing values and encode strings if needed
            model_df = df[independent + [dependent]].dropna()
            if model_df.empty:
                return {"analysis_type": intent, "error": "No valid data remaining after dropping nulls."}

            X = model_df[independent]
            y = model_df[dependent]
            
            # Simple string encoding fallback for X
            import pandas as pd
            from sklearn.preprocessing import LabelEncoder
            for col in X.columns:
                if str(X[col].dtype) in ['object', 'category', 'string']:
                    X.loc[:, col] = LabelEncoder().fit_transform(X[col].astype(str))

            # Determine whether to use Regression or Classification
            # If target is string, binary, or explicitly classification
            is_classifier = False
            if intent == "classification" or str(y.dtype) in ['object', 'category', 'string', 'bool']:
                is_classifier = True
            elif y.nunique() < 10:
                is_classifier = True
                
            if is_classifier:
                y = LabelEncoder().fit_transform(y.astype(str))
                model = LogisticRegression(max_iter=1000)
                model.fit(X, y)
                predictions = model.predict(X)
                score = accuracy_score(y, predictions)
                return {
                    "analysis_type": "logistic_regression",
                    "accuracy": float(round(score, 4)),
                    "intercept": float(round(model.intercept_[0], 4)) if hasattr(model.intercept_, '__len__') else float(round(model.intercept_, 4)),
                    "coefficients": dict(zip(independent, [round(float(c), 4) for c in model.coef_[0]])),
                }
            else:
                model = LinearRegression()
                model.fit(X, y)
                predictions = model.predict(X)
                r2 = r2_score(y, predictions)
                return {
                    "analysis_type": "linear_regression",
                    "r_squared": float(round(r2, 4)),
                    "intercept": float(round(model.intercept_[0], 4)) if hasattr(model.intercept_, '__len__') else float(round(model.intercept_, 4)),
                    "coefficients": dict(zip(independent, [round(float(c), 4) for c in model.coef_])),
                }

        raise ExecutionError(f"Sklearn does not support intent: {intent}")
