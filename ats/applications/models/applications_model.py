# ats/applications/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid


from ats.core.models import AtsBaseModel

class Application(AtsBaseModel):
    """
    Documents supplémentaires liés à une candidature (Submission)
    Relation OneToOne : une candidature = une application
    """
    
    
    submission = models.OneToOneField(
        "submissions.Submission",  # On référence Submission (à convertir ensuite si pas déjà fait)
        on_delete=models.CASCADE,
        related_name="application",  # Permet submission.application
        verbose_name=_("candidature")
    )
    
    cv_url = models.URLField(_("CV"), blank=True, null=True)
    portfolio_url = models.URLField(_("portfolio"), blank=True, null=True)
    other_documents = models.TextField(
        _("autres documents"),
        blank=True,
        null=True,
        help_text=_("Liens séparés par des virgules ou JSON : ['lien1', 'lien2']")
    )

    class Meta:
        verbose_name = _("dossier de candidature")
        verbose_name_plural = _("dossiers de candidature")

    def __str__(self):
        return f"Dossier - {self.submission}"