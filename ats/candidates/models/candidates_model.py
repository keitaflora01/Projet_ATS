# ats/candidates/models/candidates_model.py
from django.db import models
from django.utils.translation import gettext_lazy as _

from ats.core.models import AtsBaseModel


class Candidate(AtsBaseModel):
    """
    Profil minimal du candidat.
    Hérite de AtsBaseModel pour avoir created, updated, id UUID automatiquement.
    Contient uniquement la biographie (présentation libre).
    Tous les autres champs (expérience, salaire, CV, LM, portfolio, score) sont dans Application.
    """
    user = models.OneToOneField(
        "users.User",
        on_delete=models.CASCADE,
        related_name="candidate_profile",  # user.candidate_profile
        limit_choices_to={"role": "candidate"},
        verbose_name=_("utilisateur")
    )
    
    bio = models.TextField(
        _("biographie / présentation"),
        blank=True,
        help_text=_("Présentez-vous en quelques lignes (facultatif)")
    )

    profile_photo = models.ImageField(
        _("photo de profil"),
        upload_to="profiles/candidates/",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("candidat")
        verbose_name_plural = _("candidats")
        ordering = ["-created"]  # Tri par date de création (du plus récent)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.email} - Candidat"