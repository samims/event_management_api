from django.contrib.auth.models import AbstractUser


# Keeping scope to modify the user model
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    """
    Custom user model helps us to add/modify the Django provided user model
    in the future
    """
    # making email fields unique cause it makes sense :)
    email = models.EmailField(_('email address'), blank=False, unique=True)

