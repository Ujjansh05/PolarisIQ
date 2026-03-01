# planning/plan_schema.py

from pydantic import BaseModel
from typing import Optional, Dict, List


class DataScope(BaseModel):
    tables: List[str]
    filters: Optional[List[Dict]] = []


class StatisticsSpec(BaseModel):
    type: List[str]
    parameters: Dict


class PredictionSpec(BaseModel):
    type: str
    parameters: Dict


class QueryPlan(BaseModel):
    intent: str
    data_scope: DataScope
    statistics: Optional[StatisticsSpec] = None
    prediction: Optional[PredictionSpec] = None
    execution_engine: str
    explanation_level: str
