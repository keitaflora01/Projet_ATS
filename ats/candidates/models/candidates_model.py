from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid


from ats.core.models import AtsBaseModel

class Candidate(AtsBaseModel):
    
    user = models.OneToOneField(
        "users.User",  # Référence à ton modèle User custom dans l'app users
        on_delete=models.CASCADE,
        related_name="candidate_profile",  # Permet user.candidate_profile
        verbose_name=_("utilisateur")
    )
    
    phone = models.CharField(_("téléphone"), max_length=50, blank=True, null=True)
    location = models.CharField(_("localisation"), max_length=200, blank=True, null=True)
    bio = models.TextField(_("biographie"), blank=True, null=True)
    resume_url = models.URLField(_("lien vers le CV"), blank=True, null=True)
    profile_picture_url = models.URLField(_("photo de profil"), blank=True, null=True)
    
    years_of_experience = models.CharField(
        _("années d'expérience"),
        max_length=50,
        blank=True,
        null=True,
        help_text=_("Ex: '5 ans', 'Débutant', '10+'")
    )
    desired_salary = models.CharField(
        _("salaire souhaité"),
        max_length=100,
        blank=True,
        null=True,
        help_text=_("Ex: '50-60k €', 'Négociable'")
    )
    availability_date = models.DateField(
        _("date de disponibilité"),
        blank=True,
        null=True
    )
    
    

    class Meta:
        ordering = ["-created"]
        verbose_name = _("candidat")
        verbose_name_plural = _("candidats")

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.email} - Candidat"