from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext_lazy as _
from ats.core.models import AtsBaseModel


class UserManager(BaseUserManager):
    def create_user(self, email, full_name="", password=None, **extra_fields):
        if not email:
            raise ValueError("L'adresse email est obligatoire")
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name="", password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_verified", True)
        extra_fields.setdefault("role", UserRole.ADMIN)

        return self.create_user(email, full_name, password, **extra_fields)


class UserRole(models.TextChoices):
    CANDIDATE = "candidate", _("Candidat")
    RECRUITER = "recruiter", _("Recruteur")
    ADMIN = "admin", _("Administrateur")


class User(AtsBaseModel, AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_("adresse email"), unique=True)
    full_name = models.CharField(_("nom complet"), max_length=255, blank=True)
    
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.CANDIDATE,
    )
    
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    
    date_joined = models.DateTimeField(default=timezone.now)

    profile_photo = models.ImageField(
        _("photo de profil"),
        upload_to="profiles/",
        blank=True,
        null=True,
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("utilisateur")
        verbose_name_plural = _("utilisateurs")

    def __str__(self):
        return self.email or "Utilisateur sans email"

    def get_full_name(self):
        return self.full_name or self.email

    def get_short_name(self):
        return self.full_name.split()[0] if self.full_name else self.email
    
    @property
    def photo_url(self):
        """Retourne l'URL de la photo ou None (pas d'image par défaut)"""
        if self.profile_photo and self.profile_photo.url:
            return self.profile_photo.url
        return None