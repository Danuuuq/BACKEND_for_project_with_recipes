# Generated by Django 5.1.3 on 2024-11-28 07:09

import django.db.models.manager
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipe',
            options={'default_manager_name': 'tags_and_ingredients', 'default_related_name': 'recipes', 'ordering': ('name', 'id'), 'verbose_name': 'рецепт', 'verbose_name_plural': 'Рецепты'},
        ),
        migrations.AlterModelOptions(
            name='recipeingredient',
            options={'default_manager_name': 'names_ingredients', 'ordering': ('recipe', 'ingredient'), 'verbose_name': 'ингридиенты рецепта', 'verbose_name_plural': 'Ингридиенты рецептов'},
        ),
        migrations.AlterModelManagers(
            name='recipe',
            managers=[
                ('tags_and_ingredients', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='recipeingredient',
            managers=[
                ('names_ingredients', django.db.models.manager.Manager()),
            ],
        ),
    ]