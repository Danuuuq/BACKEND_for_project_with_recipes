from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from . import constants
from .managers import UserQuerySet


class User(AbstractUser):

    name_validator = RegexValidator(
        regex=constants.REGEX,
        message=(
            'Имя и Фамилия должны содержать буквенные символы '
            'или разрешенные символы `/./- и пробел'
        )
    )

    first_name = models.CharField('имя', validators=[name_validator],
                                  max_length=constants.MAX_LENGTH_NAME_USER)
    last_name = models.CharField('фамилия', validators=[name_validator],
                                 max_length=constants.MAX_LENGTH_NAME_USER)
    email = models.EmailField('Адрес электронной почты',
                              max_length=constants.MAX_LENGTH_EMAIL,
                              unique=True)
    avatar = models.ImageField('аватар', upload_to='users/images/',
                               blank=True, null=True)

    objects = UserQuerySet.as_manager()

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='followers',
                             verbose_name='подписчик')
    following = models.ForeignKey(User, on_delete=models.CASCADE,
                                  related_name='followings',
                                  verbose_name='подписка')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='Unique follower constraint'
            ),
            models.CheckConstraint(
                condition=~models.Q(following=models.F('user')),
                name='Подписка на самого себя'
            )
        ]
        ordering = ('following', 'id')
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user} подписан на {self.following}'
