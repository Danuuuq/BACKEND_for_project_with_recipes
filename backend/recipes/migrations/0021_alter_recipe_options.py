# Generated by Django 5.1.3 on 2024-11-19 18:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0020_alter_recipe_author_alter_recipe_short_url'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipe',
            options={'default_related_name': 'recipes', 'ordering': ('name', 'id'), 'verbose_name': 'рецепт', 'verbose_name_plural': 'Рецепты'},
        ),
    ]