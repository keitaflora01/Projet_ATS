
def build_prompt(template, **kwargs):
    """Remplace les placeholders dans un prompt"""
    try:
        return template.format(**kwargs)
    except KeyError as e:
        print(f"[PROMPT BUILD ERROR] Clé manquante : {e}")
        return template  

def validate_json_structure(data, required_keys):
    """Vérifie qu'un JSON a les clés obligatoires"""
    missing = [k for k in required_keys if k not in data]
    if missing:
        raise ValueError(f"Clés manquantes dans JSON : {missing}")
    return True