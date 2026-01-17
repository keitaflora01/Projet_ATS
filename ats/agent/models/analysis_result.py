# ats/agent/models/analysis_result.py
from django.db import models
from django.utils.translation import gettext_lazy as _

from ats.core.models import AtsBaseModel


class RecommendationChoice(models.TextChoices):
    INTERVIEW_HIGH = "interview_high", _("Entretien prioritaire")
    INTERVIEW_MEDIUM = "interview_medium", _("Entretien possible")
    INTERVIEW_LOW = "interview_low", _("Entretien optionnel")
    WAIT = "wait", _("À attendre / plus d'infos")
    REJECT = "reject", _("Rejet recommandé")


class AIAnalysisResult(AtsBaseModel):
    """
    Résultat complet de l'analyse IA d'une candidature.
    Stocke les sorties des agents d'extraction, matching et recommandation.
    """
    submission = models.OneToOneField(
        "submissions.Submission",
        on_delete=models.CASCADE,
        related_name="ai_analysis",
        verbose_name=_("candidature analysée")
    )

    # Agent 1 - Extraction du profil (CV + LM)
    extracted_profile = models.JSONField(
        _("profil extrait"),
        default=dict,
        help_text=_("Données structurées : compétences, expériences, diplômes, etc.")
    )

    # Agent 2 - Matching avec l'offre
    matching_score = models.PositiveSmallIntegerField(
        _("score de matching"),
        default=0,
        help_text=_("Score de 0 à 100 calculé par l'IA")
    )
    matching_details = models.JSONField(
        _("détails du matching"),
        default=dict,
        help_text=_("Compétences correspondantes, manquantes, forces/faiblesses")
    )

    # Agent 3 - Recommandation & aide à la décision
    recommendation = models.CharField(
        _("recommandation finale"),
        max_length=30,
        choices=RecommendationChoice.choices,
        default=RecommendationChoice.WAIT,
        help_text=_("Action suggérée au recruteur")
    )
    recommendation_reason = models.TextField(
        _("justification détaillée"),
        blank=True,
        help_text=_("Explication claire et concise de la recommandation")
    )

    # Métadonnées du traitement
    processed_at = models.DateTimeField(
        _("date de traitement IA"),
        auto_now_add=True
    )
    processing_duration = models.DurationField(
        _("durée du traitement"),
        null=True,
        blank=True,
        help_text=_("Temps total de calcul des 3 agents")
    )
    ai_model_version = models.CharField(
        _("version du modèle IA"),
        max_length=50,
        blank=True,
        help_text=_("Ex: 'gpt-4o-mini-2024-11', 'grok-beta'")
    )
    confidence = models.FloatField(
        _("niveau de confiance global"),
        default=0.0,
        help_text=_("Confiance de l'IA sur l'analyse (0.0 à 1.0)")
    )

    class Meta:
        verbose_name = _("résultat d'analyse IA")
        verbose_name_plural = _("résultats d'analyse IA")
        ordering = ["-processed_at"]

    def __str__(self):
        return f"IA - {self.submission} - Score: {self.matching_score}%"

    @property
    def recommendation_display(self):
        return self.get_recommendation_display()