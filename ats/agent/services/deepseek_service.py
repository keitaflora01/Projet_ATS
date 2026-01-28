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
Tu es un expert en recrutement (ATS intelligent), très strict mais juste.

OBJECTIF
- Évaluer un candidat à partir de son CV, de sa lettre (si fournie) et d’une offre d’emploi (si fournie).
- Si l’offre d’emploi est vide ou insuffisante, tu dois faire une évaluation "qualité globale du CV" (structure, clarté, cohérence, impact, compétences, expériences), au lieu de refuser l’analyse.

RÈGLES DE NOTATION
- Ne mets JAMAIS 0 sauf si le CV est vide/inexploitable/illisible.
- Si le CV est professionnel mais ne correspond pas au poste, attribue un score faible mais réaliste (ex: 5–20) en valorisant les compétences transversales (soft skills, langues, gestion, communication).
- Si le CV correspond, sois exigeant sur les détails techniques (preuves, projets, outils, niveau, résultats).
- Donne une confiance (confidence) qui reflète la qualité et la quantité d’informations disponibles.

FORMAT DE RÉPONSE (IMPORTANT)
- Retourne UNIQUEMENT un JSON valide.
- Aucun texte hors JSON. Aucun markdown. Aucune balise ```.

Structure attendue du JSON :
{
  "score": 0-100,
  "recommendation": "wait|reject|interview_low|interview_medium|interview_high",
  "summary": "Analyse concise, critique et professionnelle en français",
  "confidence": 0.0-1.0,
  "extracted_skills": ["..."],
  "matching_skills": ["..."],
  "missing_skills": ["..."]
}
"""

    user_prompt = f"""
OFFRE D'EMPLOI (peut être vide) :
{job_description[:20000]}

CV DU CANDIDAT :
{cv_text[:30000]}

LETTRE DE MOTIVATION (peut être vide) :
{cover_text[:10000]}

INSTRUCTIONS
- Produis UNIQUEMENT un JSON valide selon la structure demandée.
- Si l'offre est vide, matching_skills = points forts du CV ; missing_skills = points d'amélioration.
- Si l'offre est présente, matching_skills = compétences du CV alignées avec l'offre ; missing_skills = manques par rapport à l'offre.
"""

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,  # Lower temperature for stricter evaluation
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

def generate_interview_questions(job_description: str, cv_text: str) -> list:
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        return ["Pas de question disponible (Clé API manquante)"]

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    system_prompt = """
Tu es un recruteur expert.

OBJECTIF
- Générer 15 questions (QCM) : techniques + comportementales, basées sur le CV et l’offre.
- Si l’offre est vide, base-toi uniquement sur le CV.

RÈGLES
- Questions claires, niveau réaliste (ni trop facile, ni trop ambigu).
- 4 choix (A, B, C, D) et 1 seule bonne réponse, indiquée exactement dans "answer".
- Pas de blabla.

FORMAT (IMPORTANT)
- Retourne UNIQUEMENT une liste JSON valide (pas de texte hors JSON, pas de markdown, pas de ```).

Structure JSON attendue:
[
  {
    "question": "Texte de la question ?",
    "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
    "answer": "La bonne réponse exacte"
  }
]
"""

    user_prompt = f"""
OFFRE (peut être vide) :
{job_description[:5000]}

CV :
{cv_text[:5000]}

INSTRUCTIONS
- Retourne UNIQUEMENT du JSON valide.
- Fais 15 questions.
"""

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=3000
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.replace("```json", "").replace("```", "")
        return json.loads(content)
    except Exception as e:
        print(f"❌ Erreur DeepSeek Questions : {str(e)}")
        return [{"error": "Erreur génération questions"}]
