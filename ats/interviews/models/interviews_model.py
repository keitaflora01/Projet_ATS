# ats/interviews/models.py
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import uuid


class InterviewType(models.TextChoices):
    PHONE = "phone", _("Téléphonique")
    VIDEO = "video", _("Visio")
    ON_SITE = "on_site", _("Sur site")
    TECHNICAL = "technical", _("Technique")


class InterviewStatus(models.TextChoices):
    SCHEDULED = "scheduled", _("Planifié")
    COMPLETED = "completed", _("Terminé")
    CANCELLED = "cancelled", _("Annulé")
    NO_SHOW = "no_show", _("Absent")


class Interview(models.Model):
    """
    Entretien lié à une candidature (Submission)
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    submission = models.ForeignKey(
        "submissions.Submission",
        on_delete=models.CASCADE,
        related_name="interviews",  # submission.interviews.all()
        verbose_name=_("candidature")
    )
    
    interview_type = models.CharField(
        _("type d'entretien"),
        max_length=20,
        choices=InterviewType.choices
    )
    
    scheduled_at = models.DateTimeField(_("date et heure prévue"))
    
    location_or_link = models.CharField(
        _("lieu ou lien"),
        max_length=500,
        blank=True,
        null=True,
        help_text=_("Adresse physique ou lien Zoom/Meet/Teams")
    )
    
    notes = models.TextField(_("notes"), blank=True, null=True)
    
    status = models.CharField(
        _("statut"),
        max_length=20,
        choices=InterviewStatus.choices,
        default=InterviewStatus.SCHEDULED
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-scheduled_at"]
        verbose_name = _("entretien")
        verbose_name_plural = _("entretiens")

    def __str__(self):
        return f"{self.get_interview_type_display()} - {self.submission} ({self.scheduled_at.strftime('%d/%m/%Y %H:%M')})"