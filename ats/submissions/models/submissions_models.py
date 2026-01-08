from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import uuid


class SubmissionStatus(models.TextChoices):
    SUBMITTED = "submitted", _("Soumise")
    UNDER_REVIEW = "under_review", _("En cours d'examen")
    INTERVIEW_SCHEDULED = "interview_scheduled", _("Entretien planifié")
    REJECTED = "rejected", _("Refusée")
    ACCEPTED = "accepted", _("Acceptée")


from ats.core.models import AtsBaseModel

class Submission(AtsBaseModel):
    """
    Candidature d'un candidat à une offre d'emploi
    Lie Candidate ↔ JobOffer
    """
    
    
    candidate = models.ForeignKey(
        "candidates.Candidate",
        on_delete=models.CASCADE,
        related_name="submissions",  # candidate.submissions.all()
        verbose_name=_("candidat")
    )
    
    job_offer = models.ForeignKey(
        "jobs.JobOffer",
        on_delete=models.CASCADE,
        related_name="submissions",  # job_offer.submissions.all()
        verbose_name=_("offre d'emploi")
    )
    
    cover_letter = models.TextField(_("lettre de motivation"), blank=True, null=True)
    
    submission_status = models.CharField(
        _("statut"),
        max_length=30,
        choices=SubmissionStatus.choices,
        default=SubmissionStatus.SUBMITTED
    )
    

    class Meta:
        ordering = ["-created"]
        unique_together = ["candidate", "job_offer"]  # Un candidat ne postule qu'une fois par offre
        verbose_name = _("candidature")
        verbose_name_plural = _("candidatures")

    def __str__(self):
        return f"{self.candidate} → {self.job_offer.title} ({self.get_status_display()})"