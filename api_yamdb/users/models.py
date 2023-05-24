from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    admin = 'admin'    
    user = 'user'
    moderator = 'moderator'
    Roles = [
        (admin, 'admin'),
        (user, 'user'),
        (moderator, 'moderator'),
    ]
    
    bio = models.TextField(blank=True)

    role = models.CharField(
        max_length=32,
        choices=Roles,
        default=user,
        verbose_name='Роль'
    )

    confirmation_code = models.TextField(max_length=16, null=True,)
    author = models.TextField(max_length=16, null=True,)

    email = models.EmailField(
        max_length=254,
        unique=True,
        null=False,
    )
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

