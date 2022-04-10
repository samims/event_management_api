from django.contrib.auth.models import AbstractUser


# Keeping scope to modify the user model
class CustomUser(AbstractUser):
    """
    Custom user model helps us to add/modify the Django provided user model
    in the future
    """
    pass
