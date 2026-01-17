import json
import re

def parse_json_response(raw_text):
    """
    Nettoie et parse une réponse JSON du LLM (gère les erreurs courantes)
    """
    try:
        cleaned = re.sub(r'^```json\s*|\s*```$', '', raw_text.strip())
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        print(f"[JSON PARSE ERROR] {e} - Raw: {raw_text[:200]}...")
        return {"error": "Invalid JSON", "raw": raw_text}

def clean_text(text):
    """
    Nettoyage basique de texte extrait (supprime espaces multiples, etc.)
    """
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()