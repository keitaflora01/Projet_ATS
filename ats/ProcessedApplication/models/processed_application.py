# ats/applications/models/processed_application.py
from django.db import models
from django.utils.translation import gettext_lazy as _

from ats.core.models import AtsBaseModel


class ProcessedApplication(AtsBaseModel):
    """
    Résultats du traitement intelligent (IA) d'une candidature.
    Stocke les sorties des 3 agents après analyse en background.
    """
    application = models.OneToOneField(
        "applications.Application",
        on_delete=models.CASCADE,
        related_name="processed_result",
        verbose_name=_("candidature originale")
    )

    # Résultats Agent 1 : Extraction du profil
    extracted_profile = models.JSONField(
        _("profil extrait"),
        default=dict,
        help_text=_("Compétences, diplômes, expériences extraits")
    )

    # Résultats Agent 2 : Matching & classement
    matching_score = models.FloatField(
        _("score de matching"),
        default=0.0,
        help_text=_("Score de 0 à 100 calculé par l'IA")
    )
    matching_details = models.JSONField(
        _("détails matching"),
        default=dict,
        help_text=_("Compétences correspondantes / manquantes")
    )

    # Résultats Agent 3 : Recommandation & aide à la décision
    recommendation = models.CharField(
        _("recommandation"),
        max_length=50,
        choices=[
            ("interview", _("Entretien recommandé")),
            ("wait", _("À attendre")),
            ("reject", _("Rejet recommandé")),
        ],
        default="wait"
    )
    recommendation_reason = models.TextField(
        _("justification de la recommandation"),
        blank=True
    )

    # Métadonnées
    processed_at = models.DateTimeField(auto_now_add=True)
    is_visible_to_recruiter = models.BooleanField(
        _("visible au recruteur"),
        default=False,
        help_text=_("Devient True après la date limite de l'offre ou manuellement")
    )

    class Meta:
        verbose_name = _("candidature traitée IA")
        verbose_name_plural = _("candidatures traitées IA")
        ordering = ["-processed_at"]

    def __str__(self):
        return f"IA - {self.application.submission} (Score: {self.matching_score})"