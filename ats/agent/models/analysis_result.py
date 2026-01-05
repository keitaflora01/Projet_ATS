from django.db import models
from django.utils.translation import gettext_lazy as _


class AIAnalysisResult(models.Model):
    submission = models.OneToOneField(
        "submissions.Submission",
        on_delete=models.CASCADE,
        related_name="ai_analysis"
    )
    
    score = models.PositiveIntegerField(_("score de matching (0-100)"))
    
    extracted_skills = models.JSONField(_("compétences extraites du CV/LM"))
    matching_skills = models.JSONField(_("compétences correspondantes à l'offre"))
    missing_skills = models.JSONField(_("compétences manquantes"))
    
    summary = models.TextField(_("résumé IA"))
    
    raw_response = models.JSONField(_("réponse brute de l'agent"), null=True, blank=True)
    
    processed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _("analyse IA")
        verbose_name_plural = _("analyses IA")

    def __str__(self):
        return f"IA - {self.submission} - Score: {self.score}%"