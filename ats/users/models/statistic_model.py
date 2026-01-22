from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid


from ats.core.models import AtsBaseModel

class Statistic(AtsBaseModel):
    
    label = models.CharField(_("libellé"), max_length=200)
    value = models.CharField(
        _("valeur"),
        max_length=100,
        help_text=_("Ex: '1 247', '+50%', '98%'")
    )
    icon = models.CharField(
        _("icône"),
        max_length=100,
        blank=True,
        null=True,
        help_text=_("Classe FontAwesome, ex: fa-briefcase, fa-users, fa-chart-line")
    )
    is_dynamic = models.BooleanField(
        _("dynamique"),
        default=False,
        help_text=_("Si coché, la valeur sera calculée automatiquement en temps réel")
    )
    order = models.PositiveIntegerField(_("ordre d'affichage"), default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = _("statistique")
        verbose_name_plural = _("statistiques")

    def __str__(self):
        return f"{self.label} : {self.value}"