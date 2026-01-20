from ats.agent.models.analysis_result import AIAnalysisResult
from ats.agent.services.common.text_extractor import extract_text_from_file
from ats.agent.services.gemini_service import analyze_with_gemini

def run_full_ai_analysis(submission, cv_path, lm_path=None):
    """
    Orchestration complète : extraction + matching + recommandation avec Gemini.
    """
    print(f"[CREATOR] Début analyse pour submission {submission.id}")

    cv_text = extract_text_from_file(cv_path) if cv_path else ""
    lm_text = extract_text_from_file(lm_path) if lm_path else ""
    job_desc = submission.job_offer.description or ""

    analysis = analyze_with_gemini(cv_text, lm_text, job_desc)

    # Sauvegarde
    result = AIAnalysisResult.objects.create(
        submission=submission,
        score=analysis.get("score", 0),
        extracted_skills=analysis.get("extracted_skills", []),
        matching_skills=analysis.get("matching_skills", []),
        missing_skills=analysis.get("missing_skills", []),
        summary=analysis.get("summary", ""),
        recommendation=analysis.get("recommendation", "wait"),
        confidence=analysis.get("confidence", 0.5),
        raw_response=analysis
    )

    print(f"[CREATOR] Analyse terminée - Score: {result.score}")
    return result