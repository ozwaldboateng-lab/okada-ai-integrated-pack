def main(documents: list[dict]) -> dict:
    if not documents:
        return {
            "retrieved_count": 0,
            "grounding_confidence": 0.0,
            "chunk_conflict_rate": 0.0,
            "index_age": 0.0,
            "source_freshness": 0.0,
            "retrieval_score_distribution": 0.0,
            "chunk_redundancy": 0.0,
            "reranker_disagreement": 0.0,
        }

    freshness_values = []
    score_values = []
    duplicates = 0
    seen = set()
    conflicts = 0

    for doc in documents:
        freshness_values.append(float(doc.get("metadata", {}).get("freshness_score", 0.5)))
        score_values.append(float(doc.get("score", 0.5)))
        if doc.get("metadata", {}).get("conflict"):
            conflicts += 1
        key = (
            doc.get("metadata", {}).get("source"),
            doc.get("metadata", {}).get("chunk_id"),
            doc.get("title"),
        )
        if key in seen:
            duplicates += 1
        else:
            seen.add(key)

    freshness = sum(freshness_values) / len(freshness_values)
    score_spread = max(score_values) - min(score_values) if len(score_values) > 1 else score_values[0]

    return {
        "retrieved_count": len(documents),
        "grounding_confidence": max(0.0, 1.0 - (conflicts / len(documents))),
        "chunk_conflict_rate": conflicts / len(documents),
        "index_age": 0.0,
        "source_freshness": freshness,
        "retrieval_score_distribution": score_spread,
        "chunk_redundancy": duplicates / len(documents),
        "reranker_disagreement": 0.0,
    }
