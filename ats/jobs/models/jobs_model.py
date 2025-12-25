# ats/jobs/models/jobs_model.py
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import uuid


class JobType(models.TextChoices):
    FULL_TIME = "full_time", _("Temps plein")
    PART_TIME = "part_time", _("Temps partiel")
    CONTRACT = "contract", _("CDDC/Intérim")
    INTERNSHIP = "internship", _("Stage")
    FREELANCE = "freelance", _("Freelance")


from ats.core.models import AtsBaseModel

class JobOffer(AtsBaseModel):
    
    recruiter = models.ForeignKey(
        "recruiters.Recruiter",  # Référence à l'app recruiters
        on_delete=models.CASCADE,
        related_name="job_offers",
        verbose_name=_("recruteur")
    )
    
    title = models.CharField(_("titre"), max_length=255)
    description = models.TextField(_("description"))
    requirements = models.TextField(_("exigences"), blank=True, null=True)
    responsibilities = models.TextField(_("responsabilités"), blank=True, null=True)
    
    location = models.CharField(_("localisation"), max_length=200, blank=True, null=True)
    is_remote = models.BooleanField(_("télétravail"), default=False)
    job_type = models.CharField(
        _("type de contrat"),
        max_length=20,
        choices=JobType.choices,
        default=JobType.FULL_TIME
    )
    
    salary_min = models.DecimalField(
        _("salaire minimum"),
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True
    )
    salary_max = models.DecimalField(
        _("salaire maximum"),
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True
    )
    
    published_at = models.DateTimeField(_("date de publication"), default=timezone.now)
    expires_at = models.DateTimeField(_("date d'expiration"), blank=True, null=True)
    is_active = models.BooleanField(_("active"), default=True)
    
    

    class Meta:
        ordering = ["-published_at"]
        verbose_name = _("offre d'emploi")
        verbose_name_plural = _("offres d'emploi")

    def __str__(self):
        return f"{self.title} - {self.recruiter.company_name}"

    @property
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False