import math

def cosine_similarity(v1: list[float], v2: list[float]) -> float:
    """Calculate the cosine similarity between two float vectors.
    
    Returns a float score between -1.0 and 1.0 (or 0.0 on mismatch/error).
    """
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm_a = math.sqrt(sum(a * a for a in v1))
    norm_b = math.sqrt(sum(b * b for b in v2))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot_product / (norm_a * norm_b)


def get_file_text_representation(file: dict) -> str:
    """Format file metadata into a standard text representation string for embedding generation.
    
    Handles both JSON string and dictionary formats for the 'meta_data' key.
    """
    name = file.get("name", "")
    category = file.get("category", "Other")
    extension = file.get("extension", "")
    meta_data = file.get("meta_data")
    
    if isinstance(meta_data, dict):
        import json
        meta_data = json.dumps(meta_data)
    elif meta_data is None:
        meta_data = ""
        
    return f"Name: {name} | Category: {category} | Extension: {extension} | Metadata: {meta_data}"
