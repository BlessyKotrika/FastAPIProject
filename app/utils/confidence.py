def calculate_confidence(
    retrieval_score: float = 0.5,
    data_freshness: float = 0.5,
    weather_certainty: float = 0.5
) -> float:
    """
    Calculates a confidence score between 0 and 1.
    More weight is assigned to retrieval quality for RAG answers.
    """
    confidence = (retrieval_score * 0.7) + (data_freshness * 0.15) + (weather_certainty * 0.15)
    return round(min(max(confidence, 0.0), 1.0), 2)