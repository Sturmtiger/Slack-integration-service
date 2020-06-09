from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    ADMIN = 1
    DEVELOPER = 2
    TYPE_CHOICES = (
        (ADMIN, 'admin'),
        (DEVELOPER, 'developer'),
    )

    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                related_name='profile')
    user_type = models.IntegerField(choices=TYPE_CHOICES)

    def __str__(self):
        return self.user.username
