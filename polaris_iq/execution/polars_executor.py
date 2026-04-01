# execution/polars_executor.py

import polars as pl
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from polaris_iq.core.exceptions import ExecutionError


class PolarsExecutor:
    def __init__(self, conn):
        self.conn = conn

    def execute(self, plan: dict):

        table = plan["data_scope"]["tables"][0]
        arrow_table = self.conn.execute(f"SELECT * FROM {table}").arrow()

        df = pl.from_arrow(arrow_table)

        intent = plan["intent"]

        if intent == "feature_engineering":
            # Attempt to extract target from plan
            target = None
            stats = plan.get("statistics") or plan.get("prediction") or {}
            params = stats.get("parameters") or {}
            target = params.get("target") or params.get("dependent")
            if isinstance(target, list) and len(target) > 0:
                target = target[0]

            # Heuristic target detection if not strictly provided
            if not target or target not in df.columns:
                target_candidates = [
                    c for c in df.columns 
                    if c.lower() in ["target", "label", "class", "salary", "price", "purchased", "purchase", "churn"]
                ]
                target = target_candidates[0] if target_candidates else df.columns[-1]

            if target not in df.columns:
                return {"analysis_type": "feature_engineering", "error": f"Target '{target}' not found in dataset."}

            # Drop rows with null target
            df = df.filter(pl.col(target).is_not_null())
            if df.height == 0:
                return {"analysis_type": "feature_engineering", "error": "No valid data after removing null targets."}

            y_series = df.get_column(target)
            X_df = df.drop(target)
            
            # Simple pandas prep
            X_pd = X_df.to_pandas()
            for col in X_pd.columns:
                if X_pd[col].dtype == 'object' or str(X_pd[col].dtype) in ['string', 'category']:
                    X_pd[col] = LabelEncoder().fit_transform(X_pd[col].astype(str))
                if X_pd[col].isnull().any():
                    X_pd[col] = X_pd[col].fillna(0) # Basic imputation

            y_pd = y_series.to_pandas()
            
            is_classification = False
            if y_pd.dtype == 'object' or str(y_pd.dtype) in ['string', 'category', 'bool']:
                y_pd = LabelEncoder().fit_transform(y_pd.astype(str))
                is_classification = True
            elif y_series.n_unique() < 15:
                is_classification = True

            try:
                model_cls = RandomForestClassifier if is_classification else RandomForestRegressor
                model = model_cls(n_estimators=50, random_state=42)
                model.fit(X_pd, y_pd)
                
                importances = model.feature_importances_
                f_imp = {f: round(float(imp), 4) for f, imp in zip(X_pd.columns, importances)}
                sorted_f_imp = dict(sorted(f_imp.items(), key=lambda item: item[1], reverse=True))
                
                # Keep top 10
                top_10 = dict(list(sorted_f_imp.items())[:10])

                return {
                    "analysis_type": "feature_engineering",
                    "target_variable": target,
                    "model_type": "Classification" if is_classification else "Regression",
                    "top_feature_importances": top_10,
                    "rows_analyzed": df.height
                }
            except Exception as e:
                return {"analysis_type": "feature_engineering", "error": f"Failed: {e}"}

        raise ExecutionError(f"Polars does not support intent: {intent}")
