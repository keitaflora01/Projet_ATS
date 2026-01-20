# ats/agent/services/common/llm_client.py
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY manquante dans .env !")

genai.configure(api_key=GEMINI_API_KEY)

DEFAULT_MODEL = os.getenv("AI_MODEL_DEFAULT", "gemini-1.5-flash")

def call_llm(prompt: str, model: str = DEFAULT_MODEL, max_tokens: int = 2048, temperature: float = 0.35) -> str | None:
    """
    Appel sécurisé à Gemini.
    - Force JSON si demandé
    - Limite tokens pour quota gratuit
    - Gestion d'erreurs (quota, connexion)
    """
    try:
        model_instance = genai.GenerativeModel(
            model_name=model,
            generation_config={
                "temperature": temperature,
                "max_output_tokens": max_tokens,
                "response_mime_type": "application/json"  # Force JSON
            }
        )

        response = model_instance.generate_content(prompt)
        text = response.text.strip()

        print(f"[LLM SUCCESS] {model} - {len(text)} tokens générés")
        return text

    except Exception as e:
        str_e = str(e).lower()
        if any(x in str_e for x in ["429", "quota", "rate limit", "resourceexhausted"]):
            print("[LLM QUOTA] Limite gratuite Gemini atteinte (souvent ~500-1000/jour). Réessayez demain.")
            return None
        print(f"[LLM ERROR] {str(e)}")
        return None