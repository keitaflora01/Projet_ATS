# ats/agent/cv_Agent.py
from .services.common.text_extractor import extract_text_from_file
from .services.common.llm_client import call_llm
from .services.common.logic import parse_json_response

CV_PROMPT = """
Analyse ce CV et extrais un profil structuré.

CV brut :
{ cv_text }

Retourne JSON :
{
  "full_name": "Nom complet",
  "current_position": "Poste actuel",
  "experience_years": nombre entier,
  "skills": ["skill1", "skill2"],
  "experiences": [{"company": "", "position": "", "duration": ""}],
  "education": [{"degree": "", "school": ""}],
  "languages": ["Langue - Niveau"],
  "certifications": ["certif1"]
}
"""

class CVAgent:
    """
    Agent professionnel pour extraction du CV.
    - Gère les erreurs (fichiers vides, parsing JSON)
    - Limite tokens pour quota Gemini gratuit
    - Logs pour debug
    """
    def __init__(self, cv_path):
        self.cv_path = cv_path
        self.cv_text = None
        self.extracted_data = None

    def extract_text(self):
        """Extrait texte du CV avec gestion d'erreur."""
        try:
            self.cv_text = extract_text_from_file(self.cv_path)
            print(f"[CVAgent] Texte extrait : {len(self.cv_text)} caractères")
            return self.cv_text
        except Exception as e:
            print(f"[CVAgent ERROR] Extraction échouée : {e}")
            return ""

    def analyze(self):
        """Analyse avec Gemini, parse JSON, gère quota."""
        if not self.cv_text:
            self.extract_text()

        if not self.cv_text:
            return {"error": "Aucun texte extrait du CV"}

        prompt = CV_PROMPT.format(cv_text=self.cv_text[:10000])  # Limite quota

        raw = call_llm(prompt, model="gemini-1.5-flash", max_tokens=1000)
        if not raw:
            return {"error": "Réponse Gemini vide (quota ou erreur)"}

        self.extracted_data = parse_json_response(raw)
        if "error" in self.extracted_data:
            return self.extracted_data

        print(f"[CVAgent] Analyse réussie - Skills: {self.extracted_data.get('skills', [])[:5]}")
        return self.extracted_data

    def get_skills(self):
        """Retourne compétences ou vide."""
        return self.extracted_data.get("skills", []) if self.extracted_data else []
    