from .services.common.text_extractor import extract_text_from_file
from .services.common.llm_client import call_llm
from .services.common.logic import parse_json_response


class CVAgent:
    """
    Agent spécialisé dans l'extraction des informations d'un CV.
    Utilisé comme composant de l'Agent 1 global (extraction).
    """

    def __init__(self, cv_path):
        self.cv_path = cv_path
        self.cv_text = None
        self.extracted_data = None

    def extract_text(self):
        """Extrait le texte brut du CV"""
        self.cv_text = extract_text_from_file(self.cv_path)
        return self.cv_text

    def analyze(self):
        """Analyse le CV avec LLM et retourne un profil structuré"""
        if not self.cv_text:
            self.extract_text()

        prompt = f"""
        Tu es un expert en analyse de CV.
        Analyse ce CV et extrais les informations clés.

        CV brut :
        {self.cv_text[:10000]}

        Retourne UNIQUEMENT un JSON valide avec :
        {{
          "full_name": "Nom complet",
          "current_position": "Poste actuel",
          "experience_years": nombre entier,
          "skills": liste de compétences,
          "experiences": liste d'objets [{{ "company": "", "position": "", "duration": "" }}],
          "education": liste d'objets [{{ "degree": "", "field": "", "school": "", "year": "" }}],
          "languages": liste ["Langue - Niveau"],
          "certifications": liste de certifications
        }}
        """

        raw = call_llm(prompt)
        self.extracted_data = parse_json_response(raw)
        return self.extracted_data

    def get_skills(self):
        return self.extracted_data.get("skills", []) if self.extracted_data else []
    
    