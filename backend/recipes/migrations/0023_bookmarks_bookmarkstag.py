# Generated by Django 5.1.3 on 2024-11-20 12:33

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_initial'),
        ('recipes', '0022_remove_recipe_ingredient_remove_recipe_tag'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bookmarks',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('short_url', models.CharField(auto_created=True, max_length=6, verbose_name='Короткая ссылка')),
                ('name', models.CharField(max_length=256, verbose_name='название')),
                ('text', models.TextField(verbose_name='описание')),
                ('cooking_time', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='время готовки')),
            ],
        ),
        migrations.CreateModel(
            name='BookmarksTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bookmark', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='booktag', to='recipes.bookmarks', verbose_name='aрецепт')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tagbook', to='core.tag', verbose_name='aтег')),
            ],
            options={
                'verbose_name': 'тег asgf',
                'verbose_name_plural': 'asg рецептов',
                'ordering': ('bookmark', 'tag'),
            },
        ),
    ]
