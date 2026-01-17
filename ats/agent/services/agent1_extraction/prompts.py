EXTRACTION_PROMPT = """
Tu es un expert en recrutement spécialisé dans l'analyse de CV et lettres de motivation.

Analyse attentivement les documents suivants :

CV :
{ cv_text }

Lettre de motivation (si présente) :
{ lm_text }

Ta mission : extraire un profil candidat structuré et précis.

Retourne UNIQUEMENT un JSON valide avec cette structure exacte (pas de texte avant/après) :

{
  "full_name": "Nom complet extrait (si présent)",
  "current_position": "Poste actuel ou dernier poste connu",
  "experience_years": nombre entier (estimation, 0 si débutant),
  "skills": liste de compétences techniques et soft skills (max 15, les plus importantes),
  "experiences": liste d'objets [
    {"company": "Nom entreprise", "position": "Poste", "duration": "durée en mois ou années", "start": "année début", "end": "année fin ou 'présent'"}
  ],
  "education": liste d'objets [
    {"degree": "Diplôme", "field": "Domaine", "school": "Établissement", "year": "année obtention"}
  ],
  "languages": liste de langues avec niveau (ex: "Anglais - Avancé"),
  "certifications": liste de certifications importantes
}

Exemple de sortie attendue :
{
  "full_name": "Jean Dupont",
  "current_position": "Développeur Full Stack",
  "experience_years": 7,
  "skills": ["Python", "Django", "React", "PostgreSQL", "Docker"],
  "experiences": [...],
  "education": [...],
  "languages": ["Français - Natif", "Anglais - B2"],
  "certifications": ["AWS Certified Developer", "Scrum Master"]
}

Sois précis, évite les hallucinations, et si une info manque, mets null ou une liste vide.
"""
