# ats/agent/services/agent3_recommendation/recommender.py
import json
from ...common.llm_client import call_llm
from ...common.logic import parse_json_response
from .prompts import RECOMMENDATION_PROMPT


class Agent3Recommender:
    """
    Agent 3 : Recommandation finale pour le recruteur.
    Entrée : profil, score, détails matching, offre
    Sortie : recommandation + justification
    """

    def __init__(self, profile, score, matching_details, job_offer):
        self.profile = profile
        self.score = score
        self.matching_details = matching_details
        self.job_offer = job_offer

    def run(self):
        prompt = RECOMMENDATION_PROMPT.format(
            profile_json=json.dumps(self.profile, indent=2, ensure_ascii=False),
            score=self.score,
            matching_details_json=json.dumps(self.matching_details, indent=2, ensure_ascii=False),
            job_title=self.job_offer.title,
            job_description_short=self.job_offer.description[:800]
        )

        raw = call_llm(prompt, model="grok-beta")
        result = parse_json_response(raw)

        if "error" in result:
            return "wait", "Impossible d'obtenir une recommandation fiable."

        return result["recommendation"], result["reason"]