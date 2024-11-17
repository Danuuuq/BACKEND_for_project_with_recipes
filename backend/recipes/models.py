from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from core.models import Tag

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField('название',
                            max_length=settings.MAX_LENGTH_NAME_INGREDIENT)
    measurement_unit = models.CharField(
        'мера измерения', max_length=settings.MAX_LENGTH_MEASUREMENT_UNIT)

    class Meta:
        ordering = ('name', 'id')
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
        default_related_name = 'ingredient'


class Recipe(models.Model):
    name = models.CharField('название',
                            max_length=settings.MAX_LENGTH_NAME_RECIPE)
    text = models.TextField('описание', null=False, blank=False)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE, verbose_name='автор')
    image = models.ImageField('изображение', upload_to='recipes/images/',
                              null=False, blank=False)
    cooking_time = models.IntegerField('время готовки',
                                       validators=[MinValueValidator(1)])

    class Meta:
        ordering = ('name', 'id')
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipe'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='recipe',
                               verbose_name='рецепт')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                   related_name='ingredient',
                                   verbose_name='ингредиент')
    quantity = models.IntegerField('количество',
                                   validators=[MinValueValidator(1)])

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='Unique ingredient constraint'
            )
        ]
        ordering = ('recipe', 'ingredient')
        verbose_name = 'ингридиенты рецепта'
        verbose_name_plural = 'Ингридиенты рецептов'


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='saver', verbose_name='пользователь')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='save', verbose_name='рецепт')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='Unique save constraint'
            )
        ]
        ordering = ('recipe', 'user')
        verbose_name = 'избранное'
        verbose_name_plural = 'Избранное'


class RecipeTag(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE,
                            related_name='tag', verbose_name='тег')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='recipes', verbose_name='рецепт')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'tag'],
                name='Unique tag recipe constraint'
            )
        ]
        ordering = ('recipe', 'tag')
        verbose_name = 'тег рецепта'
        verbose_name_plural = 'Теги рецептов'
