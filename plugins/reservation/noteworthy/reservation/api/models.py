import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .managers import UserManager

class User(AbstractBaseUser):
    email = models.EmailField(_('email address'), unique=True)
    date_joined = models.DateTimeField(default=timezone.now)
    auth_code = models.UUIDField(blank=True, null=True)
    num_reservations_allowed = models.PositiveSmallIntegerField(default=1)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    base_domain = models.CharField(max_length=255)
    subdomain = models.CharField(max_length=63)

    class Meta:
        unique_together = [['base_domain', 'subdomain']]

class Link(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    wg_endpoint = models.CharField(max_length=255)
    udp_proxy_endpoint = models.CharField(max_length=255)
    wg_pubkey = models.CharField(max_length=255)
    date_created = models.DateTimeField(default=timezone.now)
