from django.db import models
from django.utils.translation import gettext_lazy as _

from ats.core.models import AtsBaseModel
from ats.users.models.user_model import User
from django.utils.html import format_html   
class Testimonial(AtsBaseModel):
    """
    Avis / Témoignage laissé par un utilisateur authentifié.
    - Lié directement à User (pas besoin de author_name séparé)
    - Note de 1 à 5 étoiles
    - Modération via is_approved
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="testimonials",
        verbose_name=_("utilisateur")
    )
    
    message = models.TextField(_("avis / témoignage"))
    
    rating = models.PositiveSmallIntegerField(
        _("note"),
        choices=[(i, f"{i} étoile{'s' if i > 1 else ''}") for i in range(1, 6)],
        default=5,
        help_text=_("Note de 1 à 5")
    )
    
    is_approved = models.BooleanField(
        _("approuvé / visible"),
        default=True,
        help_text=_("Validé par un admin pour être affiché publiquement")
    )
    
    order = models.PositiveIntegerField(
        _("ordre d'affichage"),
        default=0,
        help_text=_("Pour trier les témoignages sur la page d'accueil")
    )

    class Meta:
        ordering = ["order", "-created"]
        verbose_name = _("avis")
        verbose_name_plural = _("avis")
        indexes = [
            models.Index(fields=['is_approved', 'order']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.rating}/5"

    @property
    def short_message(self):
        return self.message[:100] + ("..." if len(self.message) > 100 else "")
    
    @property
    def profile_photo_url(self):
        if self.user.profile_photo:
            return self.user.profile_photo.url
        return None

