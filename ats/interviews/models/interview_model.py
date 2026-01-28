# ats/interviews/models/interview_model.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from ats.core.models import AtsBaseModel

class InterviewStatus(models.TextChoices):
    SCHEDULED = "scheduled", _("Planifié")
    COMPLETED = "completed", _("Terminé")
    CANCELLED = "cancelled", _("Annulé")
    PENDING_FEEDBACK = "pending_feedback", _("Attente retour")

class Interview(AtsBaseModel):
    application = models.ForeignKey(
        "applications.Application",
        on_delete=models.CASCADE,
        related_name="interviews",
        verbose_name=_("candidature")
    )
    
    job_offer = models.ForeignKey(
        "jobs.JobOffer",
        on_delete=models.CASCADE,
        related_name="interviews",
        verbose_name=_("offre d'emploi")
    )

    questions = models.JSONField(
        _("questions générées"),
        default=list,
        blank=True,
        help_text=_("Liste des questions générées par l'IA")
    )

    status = models.CharField(
        _("statut"),
        max_length=30,
        choices=InterviewStatus.choices,
        default=InterviewStatus.SCHEDULED
    )
    
    scheduled_at = models.DateTimeField(
        _("date prévue"),
        null=True,
        blank=True
    )

    class Meta:
        ordering = ["-scheduled_at"]
        verbose_name = _("entretien")
        verbose_name_plural = _("entretiens")

    def __str__(self):
        return f"Entretien {self.application.submission.candidate.get_full_name()} - {self.job_offer.title}"
