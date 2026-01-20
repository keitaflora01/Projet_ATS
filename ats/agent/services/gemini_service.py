import google.generativeai as genai
from django.conf import settings
import re

def analyze_with_gemini(cv_text: str, cover_text: str = "", job_description: str = "") -> dict:
    if not settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY manquante dans settings !")

    genai.configure(api_key=settings.GEMINI_API_KEY)

    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash-lite",
        generation_config={
            "temperature": 0.35,
            "top_p": 0.92,
            "max_output_tokens": 2048,
        }
    )

    prompt = f"""
Tu es un recruteur très objectif et précis.

CV du candidat :
{cv_text[:40000]}  # ← sécurité tokens

Lettre de motivation (si disponible) :
{cover_text[:15000]}

Offre d'emploi :
{job_description[:30000]}

Analyse la compatibilité. Réponds UNIQUEMENT avec ce format :

SCORE: 75/100
RECOMMANDATION: Entretien prioritaire
RAISONS:
• Point fort 1
• Point fort 2
• Faiblesse 1
CONFIDENCE: 82%
"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()

        result = {
            "matching_score": 50,
            "recommendation": "wait",
            "recommendation_reason": text,
            "confidence": 0.6,
        }

        # Parsing (simple mais efficace)
        if score := re.search(r'SCORE:\s*(\d+)/100', text):
            result["matching_score"] = int(score.group(1))
        
        if reco := re.search(r'RECOMMANDATION:\s*([^\n]+)', text, re.I):
            r = reco.group(1).strip().lower()
            mapping = {
                "entretien prioritaire": "interview_high",
                "entretien possible": "interview_medium",
                "à surveiller": "interview_low",
                "rejet": "reject",
            }
            result["recommendation"] = mapping.get(r, "wait")
        
        if conf := re.search(r'CONFIDENCE:\s*(\d+)%', text):
            result["confidence"] = int(conf.group(1)) / 100
        
        if reasons := re.search(r'RAISONS:(.*)', text, re.DOTALL | re.I):
            result["recommendation_reason"] = reasons.group(1).strip()

        return result

    except Exception as e:
        str_e = str(e).lower()
        if any(x in str_e for x in ["429", "quota", "rate limit", "resourceexhausted"]):
            return {
                "matching_score": 0,
                "recommendation": "wait",
                "recommendation_reason": "Limite quota gratuite Gemini atteinte aujourd'hui (souvent ~500-1000/jour). Réessayez demain.",
                "confidence": 0.0,
            }
        raise