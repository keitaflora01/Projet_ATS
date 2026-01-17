
MATCHING_PROMPT = """
Tu es un expert en recrutement tech. Tu as déjà analysé le CV et la lettre de motivation du candidat.

Voici le profil extrait du candidat :
{ profile_json }

Voici les exigences de l'offre d'emploi :
Titre : { job_title }
Description : { job_description }
Compétences requises : { required_skills }
Exigences : { requirements }

Ta mission : calculer un score de matching réaliste (0-100) et identifier les correspondances.

Retourne UNIQUEMENT un JSON valide avec cette structure :

{
  "score": nombre entier entre 0 et 100,
  "matching_skills": liste des compétences du candidat qui correspondent à l'offre,
  "missing_skills": liste des compétences exigées par l'offre mais absentes chez le candidat,
  "strengths": liste des points forts du candidat par rapport à l'offre,
  "weaknesses": liste des points faibles ou manques,
  "overall_assessment": courte phrase (max 100 mots) sur l'adéquation globale
}

Exemple :
{
  "score": 82,
  "matching_skills": ["Python", "Django", "PostgreSQL"],
  "missing_skills": ["Docker", "Kubernetes"],
  "strengths": ["5+ ans d'expérience backend", "fort en API REST"],
  "weaknesses": ["Peu d'expérience cloud", "Pas de certification AWS"],
  "overall_assessment": "Très bon profil technique, manque un peu d'expérience sur les outils DevOps modernes."
}

Sois objectif, réaliste et précis. Ne surestime pas.
"""