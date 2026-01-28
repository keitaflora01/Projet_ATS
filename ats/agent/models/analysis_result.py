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
    Stocke les sorties des agents + réponse brute de l'IA.
    """
    submission = models.OneToOneField(
        "submissions.Submission",
        on_delete=models.CASCADE,
        related_name="ai_analysis",
        verbose_name=_("candidature analysée")
    )

    extracted_profile = models.JSONField(
        _("profil extrait"),
        default=dict,
        blank=True,
        help_text=_("Compétences, expériences, diplômes, etc.")
    )

    matching_score = models.PositiveSmallIntegerField(
        _("score de matching"),
        default=0,
        help_text=_("Score final de 0 à 100")
    )

    matching_details = models.JSONField(
        _("détails matching"),
        default=dict,
        blank=True,
        help_text=_("Compétences correspondantes, manquantes, forces/faiblesses")
    )

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
        help_text=_("Explication claire et concise")
    )

    confidence = models.FloatField(
        _("niveau de confiance"),
        default=0.0,
        help_text=_("Confiance globale de l'IA (0.0 à 1.0)")
    )

    # NOUVEAUX CHAMPS POUR STOCKER LA RÉPONSE BRUTE DE L'IA (comme tu le veux)
    raw_ai_response = models.JSONField(
        _("réponse brute JSON de l'IA"),
        default=dict,
        blank=True,
        null=True,
        help_text=_("Réponse complète renvoyée par DeepSeek/Gemini - conservée pour transparence et debug")
    )

    raw_text_response = models.TextField(
        _("réponse texte brute"),
        blank=True,
        null=True,
        help_text=_("Version texte complète avant parsing - utile pour recherche")
    )

    # Métadonnées
    processed_at = models.DateTimeField(_("date de traitement"), auto_now_add=True)
    processing_duration = models.DurationField(
        _("durée du traitement"),
        null=True,
        blank=True,
        help_text=_("Temps total des agents IA")
    )
    ai_model_version = models.CharField(
        _("version du modèle IA"),
        max_length=50,
        blank=True,
        help_text=_("Ex: 'deepseek-v3'")
    )

    class Meta:
        verbose_name = _("résultat d'analyse IA")
        verbose_name_plural = _("résultats d'analyse IA")
        ordering = ["-processed_at"]
        indexes = [models.Index(fields=['submission', 'matching_score'])]

    def __str__(self):
        return f"Analyse IA - {self.submission} - Score: {self.matching_score}%"

    @property
    def recommendation_display(self):
        return self.get_recommendation_display()

    # @property
    # def score_display(self):
    #     color = "green" if self.matching_score >= 80 else "orange" if self.matching_score >= 60 else "red"
    #     return f"<strong style='color:{color};'>{self.matching_score}/100</strong>"
    # score_display.short_description = "Score"
    # score_display.allow_tags = True

