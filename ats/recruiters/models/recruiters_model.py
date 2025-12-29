# ats/recruiters/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid


from ats.core.models import AtsBaseModel

class RecruiterProfile(AtsBaseModel):
    
    user = models.OneToOneField(
        "users.User",  # Référence à ton modèle User custom dans l'app users
        on_delete=models.CASCADE,
        related_name="recruiter_profile",  # Permet user.recruiter_profile
        verbose_name=_("utilisateur")
    )
    
    company_name = models.CharField(_("nom de l'entreprise"), max_length=255)
    company_website = models.URLField(_("site web de l'entreprise"), blank=True, null=True)
    company_description = models.TextField(_("description de l'entreprise"), blank=True, null=True)
    company_logo_url = models.URLField(_("logo de l'entreprise"), blank=True, null=True)
    phone = models.CharField(_("téléphone"), max_length=50, blank=True, null=True)
    position = models.CharField(_("poste"), max_length=150, blank=True, null=True, help_text=_("Ex: Responsable RH, Talent Acquisition Manager"))

    

    class Meta:
        ordering = ["company_name"]
        verbose_name = _("recruteur")
        verbose_name_plural = _("recruteurs")

    def __str__(self):
        position = f" - {self.position}" if self.position else ""
        return f"{self.company_name}{position} ({self.user.email})"