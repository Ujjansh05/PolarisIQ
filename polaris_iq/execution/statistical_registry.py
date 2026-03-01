class StatisticalRegistry:
    SUPPORTED_OPERATIONS = {
        "linear_regression": "python_sklearn",
        "correlation": "duckdb",
        "classification": "python_sklearn",
        "aggregation": "duckdb",
    }

    @classmethod
    def get_engine(cls, operation: str):
        return cls.SUPPORTED_OPERATIONS.get(operation)
