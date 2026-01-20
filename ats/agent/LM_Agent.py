from .services.common.text_extractor import extract_text_from_file
from .services.common.llm_client import call_llm
from .services.common.logic import parse_json_response

LM_PROMPT = """
Analyse cette lettre de motivation pour extraire insights.

Lettre brut :
{ lm_text }

Retourne JSON :
{
  "motivation_level": "high" | "medium" | "low",
  "key_motivations": ["raison1", "raison2"],
  "personality_traits": ["trait1", "trait2"],
  "company_fit": "courte phrase",
  "red_flags": ["point1"]
}
"""

class LMAgent:
    """
    Agent professionnel pour analyse LM.
    - Gestion d'erreurs (fichiers vides)
    - Limite tokens
    - Logs
    """
    def __init__(self, lm_path):
        self.lm_path = lm_path
        self.lm_text = None
        self.extracted_insights = None

    def extract_text(self):
        try:
            self.lm_text = extract_text_from_file(self.lm_path)
            print(f"[LMAgent] Texte extrait : {len(self.lm_text)} caractères")
            return self.lm_text
        except Exception as e:
            print(f"[LMAgent ERROR] Extraction échouée : {e}")
            return ""

    def analyze(self):
        if not self.lm_text:
            self.extract_text()

        if not self.lm_text:
            return {"error": "Aucune lettre fournie"}

        prompt = LM_PROMPT.format(lm_text=self.lm_text[:6000])

        raw = call_llm(prompt, model="gemini-1.5-flash", max_tokens=600)
        if not raw:
            return {"error": "Réponse Gemini vide"}

        self.extracted_insights = parse_json_response(raw)
        print(f"[LMAgent] Analyse réussie - Motivation: {self.extracted_insights.get('motivation_level')}")
        return self.extracted_insights
    