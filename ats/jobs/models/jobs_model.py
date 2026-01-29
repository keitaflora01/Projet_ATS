# ats/jobs/models/jobs_model.py
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from ats.core.models import AtsBaseModel


class JobType(models.TextChoices):
    FULL_TIME = "full_time", _("Temps plein")
    PART_TIME = "part_time", _("Temps partiel")
    REMOTE = "remote", _("Télétravail 100%")
    HYBRID = "hybrid", _("Hybride")


class ContractType(models.TextChoices):
    CDI = "cdi", _("CDI")
    CDD = "cdd", _("CDD")
    ALTERNANCE = "alternance", _("Alternance")
    STAGE = "stage", _("Stage")
    FREELANCE = "freelance", _("Freelance")
    INTERIM = "interim", _("Intérim")


class JobOffer(AtsBaseModel):
    recruiter = models.ForeignKey(
        "recruiters.RecruiterProfile",
        on_delete=models.CASCADE,
        related_name="job_offers",
        verbose_name=_("recruteur")
    )
    pass_percentage = models.PositiveIntegerField(
        _("pourcentage de réussite"),
        default=70,
        help_text=_("Score minimum (0-100) pour passer à l'étape suivante")
    )
    title = models.CharField(_("titre"), max_length=255)
    description = models.TextField(_("description"))
    
    # Type de temps / rythme
    job_type = models.CharField(
        _("type de poste"),
        max_length=20,
        choices=JobType.choices,
        default=JobType.FULL_TIME
    )
    
    # Type de contrat
    contract_type = models.CharField(
        _("type de contrat"),
        max_length=20,
        choices=ContractType.choices,
        default=ContractType.CDI
    )
    
    location = models.CharField(_("localisation"), max_length=200, blank=True, null=True)
    is_remote = models.BooleanField(_("télétravail"), default=False)
    
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
    
    
    required_skills = models.TextField(_("compétences requises"), blank=True, null=True)
    requirements = models.TextField(_("exigences"), blank=True, null=True)
    
    expires_at = models.DateTimeField(_("date d'expiration"), blank=True, null=True)
    is_active = models.BooleanField(_("active"), default=True)
    
    published_at = models.DateTimeField(_("date de publication"), default=timezone.now)

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
    