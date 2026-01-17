from ats.agent.models.analysis_result import AIAnalysisResult
from ats.agent.services.agent1_extraction.extractor import Agent1Extraction
from ats.agent.services.agent2_matching.matcher import Agent2Matching
from ats.agent.services.agent3_recommendation.recommender import Agent3Recommender


def run_full_ai_analysis(submission, cv_path, lm_path=None):
    print(f"[CREATOR] Début analyse complète pour submission {submission.id}")

    agent1 = Agent1Extraction(cv_path, lm_path)
    profile = agent1.run()
    print("[Agent 1] Profil extrait")

    agent2 = Agent2Matching(profile, submission.job_offer)
    score, details = agent2.run()
    print(f"[Agent 2] Score calculé : {score}")

    agent3 = Agent3Recommender(profile, score, details, submission.job_offer)
    recommendation, reason = agent3.run()
    print(f"[Agent 3] Recommandation : {recommendation}")

    analysis = AIAnalysisResult.objects.create(
        submission=submission,
        score=score,
        extracted_skills=profile.get("skills", []),
        matching_skills=details.get("matching", []),
        missing_skills=details.get("missing", []),
        summary=reason,
        recommendation=recommendation,
        raw_response={"profile": profile, "details": details}
    )

    print(f"[CREATOR] Analyse terminée - Score: {score}")
    return analysis