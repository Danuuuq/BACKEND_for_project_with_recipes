# Generated by Django 3.2.3 on 2024-11-19 10:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_auto_20241118_1401'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='short_url',
            field=models.CharField(auto_created=True, default='None', max_length=6, verbose_name='Короткая ссылка'),
        ),
    ]
