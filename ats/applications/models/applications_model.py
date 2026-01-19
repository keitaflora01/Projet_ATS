# ats/applications/models/applications_model.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator

from ats.core.models import AtsBaseModel


class ApplicationStatus(models.TextChoices):
    PENDING = "pending", _("En attente")
    SHORTLISTED = "shortlisted", _("Pré-sélectionné")
    INTERVIEW = "interview", _("Entretien planifié")
    REJECTED = "rejected", _("Rejeté")
    ACCEPTED = "accepted", _("Accepté")


class Application(AtsBaseModel):
    """
    Dossier complet de candidature.
    Les agents IA mettront à jour status, ia_score et resume automatiquement.
    """
    submission = models.OneToOneField(
        "submissions.Submission",
        on_delete=models.CASCADE,
        related_name="application",
        verbose_name=_("candidature")
    )
    
    # Champs remplis par le candidat
    years_experience = models.PositiveIntegerField(
        _("années d'expérience"),
        null=True,
        blank=True,
        help_text=_("Ex: 5")
    )
    
    availability_date = models.DateField(
        _("date de disponibilité"),
        null=True,
        blank=True
    )
    
    desired_salary = models.DecimalField(
        _("salaire souhaité"),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("En € brut annuel")
    )
    
    portfolio_url = models.URLField(
        _("lien portfolio"),
        blank=True,
        null=True
    )
    
    cv_file = models.FileField(
        _("CV"),
        upload_to="applications/cv/",
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx', 'doc', 'odt'])],
        help_text=_("PDF, Word ou OpenDocument")
    )
    
    cover_letter_file = models.FileField(
        _("lettre de motivation"),
        upload_to="applications/cover_letters/",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx', 'doc', 'odt'])],
        help_text=_("Optionnel")
    )
    
    other_documents = models.TextField(
        _("autres documents"),
        blank=True,
        null=True,
        help_text=_("Liens supplémentaires séparés par virgule")
    )
    
    # Champs mis à jour par les agents IA
    status = models.CharField(
        _("statut de la candidature"),
        max_length=30,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.PENDING,
        help_text=_("Mis à jour automatiquement par l'IA")
    )
    
    ia_score = models.FloatField(
        _("score IA"),
        default=0.0,
        help_text=_("Score de matching calculé par l'IA (0-100)")
    )
    
    resume = models.TextField(
        _("résumé IA"),
        blank=True,
        help_text=_("Bref aperçu des compétences par rapport à l'offre (généré par l'IA)")
    )

    class Meta:
        verbose_name = _("dossier de candidature")
        verbose_name_plural = _("dossiers de candidature")

    def __str__(self):
        return f"Dossier - {self.submission}"
