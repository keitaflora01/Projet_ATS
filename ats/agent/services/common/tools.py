def truncate_text(text: str, max_length: int = 10000) -> str:
    """Tronque texte pour éviter overflow LLM."""
    if len(text) > max_length:
        return text[:max_length] + "... [tronqué]"
    return text

def safe_get(obj, key, default=None):
    """Récupération sûre d'une clé (dict ou None)."""
    if isinstance(obj, dict):
        return obj.get(key, default)
    return default