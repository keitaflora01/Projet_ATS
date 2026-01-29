from django.db import models
from django.utils.translation import gettext_lazy as _

from ats.core.models import AtsBaseModel

class SubmissionStatus(models.TextChoices):
    SUBMITTED = "submitted", _("Soumise")
    UNDER_REVIEW = "under_review", _("En cours d'examen")
    INTERVIEW_SCHEDULED = "interview_scheduled", _("Entretien planifié")
    REJECTED = "rejected", _("Refusée")
    ACCEPTED = "accepted", _("Acceptée")

class Submission(AtsBaseModel):
    """
    Lien simple entre un candidat et une offre d'emploi.
    Une candidature = une Submission.
    Les détails (CV, LM, expérience, salaire, score IA) sont dans Application (OneToOne).
    """
    
    candidate = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        limit_choices_to={"role": "candidate"},
        related_name="submissions",
        verbose_name=_("candidat")
    )
    
    job_offer = models.ForeignKey(
        "jobs.JobOffer",
        on_delete=models.CASCADE,
        related_name="submissions",
        verbose_name=_("offre d'emploi")
    )
    
    status = models.CharField(
        _("statut"),
        max_length=30,
        choices=SubmissionStatus.choices,
        default=SubmissionStatus.SUBMITTED
    )

    class Meta:
        ordering = ["-created"]
        unique_together = ["candidate", "job_offer"]  
        verbose_name = _("candidature")
        verbose_name_plural = _("candidatures")

    def __str__(self):
        return f"{self.candidate.get_full_name() or self.candidate.email} → {self.job_offer.title} ({self.get_status_display()})"