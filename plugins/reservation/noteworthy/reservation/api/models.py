import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .managers import BetaUserManager

class BetaUser(AbstractBaseUser):
    email = models.EmailField(_('email address'), unique=True)
    date_joined = models.DateTimeField(default=timezone.now)
    beta_key = models.UUIDField(blank=True, null=True)
    num_links_allowed = models.PositiveSmallIntegerField(default=1)
    num_sites_allowed = models.PositiveSmallIntegerField(default=2)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = BetaUserManager()

    def __str__(self):
        return self.email

class BetaLink(models.Model):
    beta_user = models.ForeignKey(BetaUser, on_delete=models.CASCADE)
    base_domain = models.CharField(max_length=255)
    subdomain = models.CharField(max_length=63)

    class Meta:
        unique_together = [['base_domain', 'subdomain']]

class BetaSite(models.Model):
    beta_user = models.ForeignKey(BetaUser, on_delete=models.CASCADE)
    beta_link = models.ForeignKey(BetaLink, on_delete=models.CASCADE)
    site = models.CharField(max_length=255)
