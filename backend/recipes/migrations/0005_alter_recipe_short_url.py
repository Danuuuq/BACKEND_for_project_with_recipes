# Generated by Django 5.1.3 on 2024-11-23 15:39

import recipes.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_alter_purchaseuser_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='short_url',
            field=models.CharField(default=recipes.models.Recipe.create_short_link, editable=False, max_length=6, unique=True, verbose_name='Короткая ссылка'),
        ),
    ]
