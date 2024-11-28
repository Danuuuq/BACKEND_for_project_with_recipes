from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class UserQuerySet(models.QuerySet, UserManager):

    def with_related_data(self):
        return self.prefetch_related('follower', 'recipes')

    def is_subscribe(self, user):
        return self.annotate(is_subscribed=models.Exists(
            user.follower.filter(following=models.OuterRef('pk'))))


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

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='follower',
                             verbose_name='подписчик')
    following = models.ForeignKey(User, on_delete=models.CASCADE,
                                  related_name='following',
                                  verbose_name='подписка')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='Unique follower constraint'
            )
        ]
        ordering = ('following', 'id')
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user} подписан на {self.following}'
