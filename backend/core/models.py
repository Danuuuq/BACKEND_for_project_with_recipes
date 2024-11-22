from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


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


class Tag(models.Model):
    name = models.CharField('название', unique=True,
                            max_length=settings.MAX_LENGTH_TAG)
    slug = models.SlugField('slug название', unique=True,
                            max_length=settings.MAX_LENGTH_TAG)

    class Meta:
        ordering = ('name', 'id')
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'
        default_related_name = 'tag'

    def __str__(self):
        return self.name
