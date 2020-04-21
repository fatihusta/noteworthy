import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .managers import BetaUserManager


class Reservation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    domain = models.CharField(max_length=255)

class BetaUser(AbstractBaseUser):
    email = models.EmailField(_('email address'), unique=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = BetaUserManager()

    def __str__(self):
        return self.email
