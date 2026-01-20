# ats/agent/services/common/logic.py
import json
import re

def parse_json_response(raw_text: str) -> dict:
    """
    Parse une réponse JSON du LLM, même si mal formatée (markdown, texte parasite).
    """
    try:
        # Enlève markdown ```json ... ```
        cleaned = re.sub(r'^```json\s*|\s*```$', '', raw_text.strip(), flags=re.IGNORECASE | re.DOTALL)
        data = json.loads(cleaned)
        print(f"[LOGIC] JSON parsé avec succès - clés: {list(data.keys())}")
        return data
    except json.JSONDecodeError as e:
        print(f"[LOGIC PARSE ERROR] {e} - Raw (premiers 200 chars): {raw_text[:200]}...")
        return {"error": "Invalid JSON", "raw": raw_text}

def clean_text(text: str) -> str:
    """
    Nettoyage texte extrait (supprime espaces multiples, caractères invisibles).
    """
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()
