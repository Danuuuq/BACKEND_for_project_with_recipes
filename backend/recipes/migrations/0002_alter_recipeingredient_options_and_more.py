# Generated by Django 5.1.3 on 2024-11-21 18:44

import django.db.models.manager
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipeingredient',
            options={'default_manager_name': 'published', 'ordering': ('recipe', 'ingredient'), 'verbose_name': 'ингридиенты рецепта', 'verbose_name_plural': 'Ингридиенты рецептов'},
        ),
        migrations.AlterModelManagers(
            name='recipeingredient',
            managers=[
                ('published', django.db.models.manager.Manager()),
            ],
        ),
    ]
