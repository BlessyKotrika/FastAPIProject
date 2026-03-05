def calculate_confidence(retrieval_score: float = 1.0, data_freshness: float = 1.0, weather_certainty: float = 1.0) -> float:
    """
    Calculates a confidence score between 0 and 1.
    """
    # Simple weighted average
    confidence = (retrieval_score * 0.5) + (data_freshness * 0.2) + (weather_certainty * 0.3)
    return round(min(max(confidence, 0.0), 1.0), 2)
