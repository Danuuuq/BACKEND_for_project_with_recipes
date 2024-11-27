from django.contrib.auth.models import AbstractUser, UserManager
from django.db.models import Exists, OuterRef
from django.conf import settings
from django.db import models


class UserQuerySet(models.QuerySet, UserManager):

    def with_related_data(self):
        return self.prefetch_related('follower')

    def is_subscribe(self, user):
        subscribe = user.follower.filter(following=OuterRef('pk'))
        queryset = self.annotate(is_subscribed=Exists(subscribe))
        return queryset


class UserManager(models.Manager):
    def get_queryset(self):
        return (
            UserQuerySet(self.model)
            .with_related_data()
            .is_subscribe()
        )


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

    objects = UserQuerySet.as_manager()
    
    subscribe = UserManager()

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
