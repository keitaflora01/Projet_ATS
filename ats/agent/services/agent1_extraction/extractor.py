from ...common.tools import extract_text_from_file, call_llm  
from ...common.logic import parse_json_response  
from .prompts import EXTRACTION_PROMPT


class Agent1Extraction:
    """
    Agent 1 : Extraction de profil à partir de CV et lettre de motivation.
    Entrée : chemins des fichiers CV + LM (optionnel)
    Sortie : dictionnaire structuré JSON du profil candidat
    """
    def __init__(self, cv_path, lm_path=None):
        self.cv_text = extract_text_from_file(cv_path)
        self.lm_text = extract_text_from_file(lm_path) if lm_path else ""
        self.profile = None

    def run(self):
        """Exécute l'analyse complète et retourne le profil extrait"""
        prompt = EXTRACTION_PROMPT.format(
            cv_text=self.cv_text[:12000],  # limite pour éviter token overflow
            lm_text=self.lm_text[:6000] if self.lm_text else ""
        )

        raw_response = call_llm(prompt, model="grok-beta")  # ou ton LLM préféré

        try:
            self.profile = parse_json_response(raw_response)
        except Exception as e:
            print(f"[Agent1] Erreur parsing JSON : {e}")
            self.profile = {"error": "Échec de l'extraction", "raw": raw_response}

        return self.profile

    def get_skills(self):
        """Accès rapide aux compétences extraites"""
        if self.profile:
            return self.profile.get("skills", [])
        return []