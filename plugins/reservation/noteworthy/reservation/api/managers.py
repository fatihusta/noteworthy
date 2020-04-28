from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import ugettext_lazy as _
import uuid


class UserManager(BaseUserManager):
    def create_user(self, email, **extra_fields):
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_unusable_password()
        user.save()
        return user

    def keyless_users(self):
        return self.get_queryset().filter(auth_code__isnull=True)

    def provision_auth_codes(self, num_codes):
        users = self.keyless_users().order_by('date_joined')[:num_codes]
        for user in users:
            user.auth_code = uuid.uuid4()
            user.save()
        return users
