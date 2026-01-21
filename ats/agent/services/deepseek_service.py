import os
import re
import json
from django.conf import settings
from openai import OpenAI


def analyze_with_deepseek(cv_text: str, cover_text: str = "", job_description: str = "") -> dict:
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("⚠️ DEEPSEEK_API_KEY manquante dans l'environnement !")
        # Fallback fictif pour éviter de bloquer si la clé manque temporairement
        return {
            "score": 0,
            "recommendation": "wait",
            "summary": "Clé API manquante - impossible d'analyser",
            "confidence": 0.0,
            "extracted_skills": [],
            "matching_skills": [],
            "missing_skills": []
        }

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com"
    )

    system_prompt = """
Tu es un expert en recrutement (ATS intelligent). Ta tâche est d'analyser un candidat par rapport à une offre d'emploi.
Tu DOIS répondre UNIQUEMENT au format JSON valide, sans markdown, sans explications avant ou après.

Structure attendue du JSON :
{
    "score": [entier 0-100],
    "recommendation": "[wait|reject|interview_low|interview_medium|interview_high]",
    "summary": "[Analyse concise et professionnelle en français]",
    "confidence": [float 0.0-1.0],
    "extracted_skills": ["ski1", "skill2"...],
    "matching_skills": ["skill_ok1", "skill_ok2"...],
    "missing_skills": ["skill_missing1", "skill_missing2"...]
}
"""

    user_prompt = f"""
OFFRE D'EMPLOI:
{job_description[:20000]}

CV CANDIDAT:
{cv_text[:30000]}

LETTRE MOTIVATION:
{cover_text[:10000]}
"""

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            max_tokens=2048,
            stream=False
        )

        content = response.choices[0].message.content.strip()
        
        # Nettoyage si le modèle met quand même du markdown ```json ... ```
        if content.startswith("```"):
            content = content.replace("```json", "").replace("```", "")

        data = json.loads(content)
        
        # Normalisation des clés pour éviter les crashs si le modèle hallucine un format
        return {
            "score": data.get("score", 0),
            "recommendation": data.get("recommendation", "wait"),
            "summary": data.get("summary", "Analyse effectuée."),
            "confidence": data.get("confidence", 0.5),
            "extracted_skills": data.get("extracted_skills", []),
            "matching_skills": data.get("matching_skills", []),
            "missing_skills": data.get("missing_skills", []),
        }

    except Exception as e:
        print(f"❌ Erreur DeepSeek : {str(e)}")
        return {
            "score": 0,
            "recommendation": "wait",
            "summary": f"Erreur lors de l'analyse IA : {str(e)}",
            "confidence": 0.0,
            "extracted_skills": [],
            "matching_skills": [],
            "missing_skills": []
        }
