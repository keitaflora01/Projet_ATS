# ats/applications/models/applications_model.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator

from ats.core.models import AtsBaseModel

class Application(AtsBaseModel):
    """
    Dossier complet de candidature (tout ce que le candidat fournit pour postuler)
    Lié 1-to-1 à une Submission (une candidature à une offre)
    """
    submission = models.OneToOneField(
        "submissions.Submission",
        on_delete=models.CASCADE,
        related_name="application",
        verbose_name=_("candidature")
    )
    
    # Champs du candidat pour cette candidature
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
        _("lien portfolio (GitHub, site personnel, etc.)"),
        blank=True,
        null=True
    )
    
    # Fichiers uploadés
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
    
    # Score IA (calculé automatiquement)
    ia_score = models.FloatField(
        _("score IA"),
        default=0.0,
        help_text=_("Score de matching calculé par l'IA (0-100)")
    )
    
    other_documents = models.TextField(
        _("autres documents"),
        blank=True,
        null=True,
        help_text=_("Liens supplémentaires séparés par virgule")
    )

    class Meta:
        verbose_name = _("dossier de candidature")
        verbose_name_plural = _("dossiers de candidature")

    def __str__(self):
        return f"Dossier - {self.submission}"