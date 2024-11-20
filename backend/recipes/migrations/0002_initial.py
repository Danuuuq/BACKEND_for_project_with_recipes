# Generated by Django 5.1.3 on 2024-11-20 13:59

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("core", "0002_initial"),
        ("recipes", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="recipe",
            name="author",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
                verbose_name="автор",
            ),
        ),
        migrations.AddField(
            model_name="recipeingredient",
            name="ingredient",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="ingredientrecipe",
                to="recipes.ingredient",
                verbose_name="ингредиент",
            ),
        ),
        migrations.AddField(
            model_name="recipeingredient",
            name="recipe",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="recipeingredient",
                to="recipes.recipe",
                verbose_name="рецепт",
            ),
        ),
        migrations.AddField(
            model_name="recipe",
            name="ingredient",
            field=models.ManyToManyField(
                through="recipes.RecipeIngredient", to="recipes.ingredient"
            ),
        ),
        migrations.AddField(
            model_name="recipetag",
            name="recipe",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="recipetag",
                to="recipes.recipe",
                verbose_name="рецепт",
            ),
        ),
        migrations.AddField(
            model_name="recipetag",
            name="tag",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="tagrecipe",
                to="core.tag",
                verbose_name="тег",
            ),
        ),
        migrations.AddField(
            model_name="recipe",
            name="tag",
            field=models.ManyToManyField(through="recipes.RecipeTag", to="core.tag"),
        ),
        migrations.AddConstraint(
            model_name="recipeingredient",
            constraint=models.UniqueConstraint(
                fields=("recipe", "ingredient"), name="Unique ingredient constraint"
            ),
        ),
        migrations.AddConstraint(
            model_name="recipetag",
            constraint=models.UniqueConstraint(
                fields=("recipe", "tag"), name="Unique tag recipe constraint"
            ),
        ),
    ]
