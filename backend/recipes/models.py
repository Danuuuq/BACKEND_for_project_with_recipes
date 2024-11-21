import random

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from core.models import Tag

User = get_user_model()


class IngredientQuerySet(models.QuerySet):

    def with_related_data(self):
        return self.prefetch_related('ingredient')


class IngredientManager(models.Manager):
    
    def get_queryset(self):
        return IngredientQuerySet(self.model).with_related_data()


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
    ingredient = models.ManyToManyField(Ingredient, through='RecipeIngredient')
    short_url = models.CharField('Короткая ссылка', auto_created=True,
                                 max_length=settings.MAX_LENGTH_SHORT_URL)
    tag = models.ManyToManyField(Tag, through='RecipeTag')

    def save(self, *args, **kwargs):
        while True:
            self.short_url = ''.join(
                random.choices(settings.SYMBOLS_FOR_SHORT_URL,
                               k=settings.MAX_LENGTH_SHORT_URL))
            if not Recipe.objects.filter(short_url=self.short_url).exists():
                break
        super(Recipe, self).save(*args, **kwargs)

    class Meta:
        ordering = ('name', 'id')
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipes'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='recipeingredient',
                               verbose_name='рецепт')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                   related_name='ingredientrecipe',
                                   verbose_name='ингредиент')
    amount = models.IntegerField('количество',
                                 validators=[MinValueValidator(1)])

    objects = IngredientQuerySet.as_manager()
    published = IngredientManager()

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
        default_manager_name = 'published'


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='saver', verbose_name='пользователь')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='favorite', verbose_name='рецепт')

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
                            related_name='tagrecipe', verbose_name='тег')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='recipetag', verbose_name='рецепт')

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


class PurchaseUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='buyer', verbose_name='пользователь')
    purchase = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                                 related_name='purchase', verbose_name='рецепт')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'purchase'],
                name='Unique purchase constraint'
            )
        ]
        ordering = ('purchase', 'user')
        verbose_name = 'покупки пользователя'
        verbose_name_plural = 'Покупки пользователей'
