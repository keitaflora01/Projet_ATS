from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid


from ats.core.models import AtsBaseModel

class Policy(AtsBaseModel):
    
    slug = models.SlugField(
        _("slug"),
        unique=True,
        max_length=100,
        help_text=_("Utilisé dans l'URL, ex: privacy, terms, cookies")
    )
    title = models.CharField(_("titre"), max_length=200)
    content = models.TextField(_("contenu"))
    version = models.CharField(_("version"), max_length=50, blank=True, null=True)
    is_active = models.BooleanField(_("active"), default=True)
    
    

    class Meta:
        ordering = ["slug"]
        verbose_name = _("politique")
        verbose_name_plural = _("politiques")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return f"/policies/{self.slug}/"