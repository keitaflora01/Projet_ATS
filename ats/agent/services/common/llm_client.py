import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("AI_MODEL_DEFAULT", "gemini-1.5-flash")

# Configuration globale
genai.configure(api_key=GEMINI_API_KEY)

def call_llm(prompt, model=MODEL, max_tokens=2000, temperature=0.3):
    """
    Appel au modèle Gemini.
    Retourne le contenu de la réponse.
    """
    try:
        # Création du modèle
        model_instance = genai.GenerativeModel(
            model_name=model,
            generation_config={
                "temperature": temperature,
                "max_output_tokens": max_tokens,
                "response_mime_type": "application/json"  # Force JSON
            }
        )

        # Génération
        response = model_instance.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        print(f"[GEMINI ERROR] {str(e)}")
        return None