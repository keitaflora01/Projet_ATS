# ats/users/models/service_model.py
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class Service(models.Model):
    """
    Services mis en avant sur la page d'accueil (ex: pour candidats ou recruteurs)
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    title = models.CharField(_("titre"), max_length=200)
    description = models.TextField(_("description"))
    icon = models.CharField(
        _("icône"),
        max_length=100,
        blank=True,
        help_text=_("Nom de classe FontAwesome, ex: fa-briefcase, fa-search, fa-users")
    )
    target = models.CharField(
        _("cible"),
        max_length=20,
        choices=[
            ("candidate", _("Candidat")),
            ("recruiter", _("Recruteur")),
            ("both", _("Les deux")),
        ],
        default="both",
    )
    order = models.PositiveIntegerField(_("ordre d'affichage"), default=0)
    is_active = models.BooleanField(_("actif"), default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "title"]
        verbose_name = _("service")
        verbose_name_plural = _("services")

    def __str__(self):
        return self.title