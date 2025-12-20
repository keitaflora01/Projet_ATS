# ats/users/models/testimonial_model.py
from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid


class Testimonial(models.Model):
    """
    Témoignages affichés sur le site (page d'accueil ou section dédiée)
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    author_name = models.CharField(_("nom de l'auteur"), max_length=200)
    author_role = models.CharField(_("poste/fonction"), max_length=150, blank=True, null=True)
    company = models.CharField(_("entreprise"), max_length=200, blank=True, null=True)
    content = models.TextField(_("témoignage"))
    rating = models.PositiveSmallIntegerField(
        _("note"),
        default=5,
        choices=[(i, f"{i} étoile{'s' if i > 1 else ''}") for i in range(1, 6)]
    )
    photo_url = models.URLField(_("photo de l'auteur"), blank=True, null=True)
    is_approved = models.BooleanField(_("approuvé"), default=False)
    order = models.PositiveIntegerField(_("ordre d'affichage"), default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "-created_at"]
        verbose_name = _("témoignage")
        verbose_name_plural = _("témoignages")

    def __str__(self):
        return f"{self.author_name} ({self.company or 'Particulier'}) - {self.rating}/5"