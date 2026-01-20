import json
from ...common.llm_client import call_llm
from ...common.logic import parse_json_response
from .prompts import MATCHING_PROMPT


class Agent2Matching:# tes outils existants
    """
    Agent 2 : Matching du profil candidat avec l'offre d'emploi.
    Entrée : profil extrait (dict) + objet JobOffer
    Sortie : score + détails matching
    """

    def __init__(self, profile, job_offer):
        self.profile = profile
        self.job_offer = job_offer

    def run(self):
        prompt = MATCHING_PROMPT.format(
            profile_json=json.dumps(self.profile, indent=2, ensure_ascii=False),
            job_title=self.job_offer.title,
            job_description=self.job_offer.description[:2000],
            required_skills=self.job_offer.required_skills or "Non spécifiées",
            requirements=self.job_offer.requirements or "Non spécifiées"
        )

        raw = call_llm(prompt, model="grok-beta")
        result = parse_json_response(raw)

        if "error" in result:
            return 0, {"error": result["error"]}

        return result["score"], {
            "matching": result["matching_skills"],
            "missing": result["missing_skills"],
            "strengths": result["strengths"],
            "weaknesses": result["weaknesses"],
            "assessment": result["overall_assessment"]
        }