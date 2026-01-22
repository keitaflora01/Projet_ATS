import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


from ats.core.models import AtsBaseModel

class Service(AtsBaseModel):
    
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
    
    

    class Meta:
        ordering = ["order", "title"]
        verbose_name = _("service")
        verbose_name_plural = _("services")

    def __str__(self):
        return self.title