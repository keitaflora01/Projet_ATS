from .services.common.text_extractor import extract_text_from_file
from .services.common.llm_client import call_llm
from .services.common.logic import parse_json_response


class LMAgent:
    """
    Agent spécialisé dans l'analyse de la lettre de motivation.
    Complète l'extraction du profil en détectant motivation, personnalité et fit culturel.
    """

    def __init__(self, lm_path):
        self.lm_path = lm_path
        self.lm_text = None
        self.extracted_insights = None

    def extract_text(self):
        self.lm_text = extract_text_from_file(self.lm_path)
        return self.lm_text

    def analyze(self):
        if not self.lm_text:
            self.extract_text()

        prompt = f"""
        Tu es un recruteur expert en lecture de lettres de motivation.

        Analyse cette lettre :

        {self.lm_text[:6000]}

        Retourne UNIQUEMENT un JSON avec :
        {{
          "motivation_level": "fort" | "moyen" | "faible",
          "key_motivations": liste de raisons mentionnées pour postuler,
          "personality_traits": liste de traits de personnalité perçus,
          "company_fit": phrase sur l'adéquation avec l'entreprise,
          "red_flags": liste de points négatifs ou incohérences (si présents)
        }}
        """

        raw = call_llm(prompt)
        self.extracted_insights = parse_json_response(raw)
        return self.extracted_insights
    