from django.db import models

from users.models import User
from recipes.models import Recipe


class PurchaseUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='buyer', verbose_name='пользователь')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='purchase', verbose_name='рецепт')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='Unique purchase constraint'
            )
        ]
        ordering = ('recipe', 'user')
        verbose_name = 'покупки пользователя'
        verbose_name_plural = 'Покупки пользователей'
