# Generated by Django 3.2.3 on 2024-11-19 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0007_alter_recipe_short_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='short_url',
            field=models.CharField(max_length=6, unique=True, verbose_name='Короткая ссылка'),
        ),
    ]