import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .managers import BetaUserManager

class BetaUser(AbstractBaseUser):
    email = models.EmailField(_('email address'), unique=True)
    date_joined = models.DateTimeField(default=timezone.now)
    beta_key = models.UUIDField(blank = True, null = True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = BetaUserManager()

    def __str__(self):
        return self.email

class BetaReservation(models.Model):
    beta_user = models.ForeignKey(BetaUser, on_delete=models.CASCADE, unique=True)
    domain = models.CharField(max_length=255, unique=True)
