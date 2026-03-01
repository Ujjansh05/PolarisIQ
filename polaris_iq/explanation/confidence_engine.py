class ConfidenceEngine:
    def score(self, result: dict):

        if "r_squared" in result:
            r2 = result["r_squared"]
            if r2 > 0.8:
                return "High"
            elif r2 > 0.5:
                return "Moderate"
            else:
                return "Low"

        return "Unknown"
