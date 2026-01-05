# ats/applications/models/applications_model.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator
import uuid

from ats.core.models import AtsBaseModel

class Application(AtsBaseModel):
    """
    Documents uploadés par le candidat pour une candidature
    """
    submission = models.OneToOneField(
        "submissions.Submission",
        on_delete=models.CASCADE,
        related_name="application",
        verbose_name=_("candidature")
    )
    
    cv_file = models.FileField(
        _("CV"),
        upload_to="applications/cv/",
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx', 'doc'])],
        help_text=_("PDF ou Word uniquement, max 10 Mo")
    )
    
    cover_letter_file = models.FileField(
        _("Lettre de motivation"),
        upload_to="applications/cover_letters/",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx', 'doc'])],
        help_text=_("PDF ou Word, optionnel")
    )
    
    portfolio_url = models.URLField(_("portfolio (GitHub, site, etc.)"), blank=True, null=True)
    
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