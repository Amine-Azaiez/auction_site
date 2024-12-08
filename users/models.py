from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # You can add additional fields here if needed

    avatar = models.ImageField(upload_to='auction_pictures/avatars/', default='auction_pictures/avatars/default-avatar1.png')
    pass

    class Meta:
        permissions = [
            # Custom permissions can be added here if needed
        ]

    