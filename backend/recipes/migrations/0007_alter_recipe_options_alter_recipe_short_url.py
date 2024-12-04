# Generated by Django 5.1.3 on 2024-12-04 13:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0006_alter_recipe_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipe',
            options={'default_manager_name': 'tags_and_ingredients', 'default_related_name': 'recipes', 'ordering': ('-created_at', 'name'), 'verbose_name': 'рецепт', 'verbose_name_plural': 'Рецепты'},
        ),
        migrations.AlterField(
            model_name='recipe',
            name='short_url',
            field=models.CharField(editable=False, max_length=6, unique=True, verbose_name='Короткая ссылка'),
        ),
    ]
