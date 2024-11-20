from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models

from .managers import UserManager

class User(AbstractUser):
    first_name = models.CharField('имя',
                                  max_length=settings.MAX_LENGTH_NAME_USER)
    last_name = models.CharField('фамилия',
                                 max_length=settings.MAX_LENGTH_NAME_USER)
    email = models.EmailField('Адрес электронной почты',
                              max_length=settings.MAX_LENGTH_EMAIL,
                              unique=True)
    avatar = models.ImageField('аватар', upload_to='users/images/',
                               blank=True, default=None)

    class Meta:
        # ordering = ('username', 'id')
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        # default_related_name = 'user'
