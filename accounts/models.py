from django.contrib.auth.models import AbstractUser


# Keeping scope to modify the user model
from django.core.validators import validate_email
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    """
    Custom user model helps us to add/modify the Django provided user model
    in the future
    """
    # making email fields unique cause it makes sense :)
    email = models.EmailField(_('email address'), blank=False, unique=True, validators=[validate_email])

    def __str__(self):
        return self.email

    # validate the email field
    def clean(self):
        """
        Validate the email field to make sure it is a valid email address.
        for some weird reason, django does not validate the email field on creation
        """
        validate_email(self.email)
        super(CustomUser, self).clean()

    def save(self, *args, **kwargs):
        self.clean()
        return super(CustomUser, self).save(*args, **kwargs)


