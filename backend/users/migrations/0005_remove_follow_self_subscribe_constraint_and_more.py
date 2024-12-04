# Generated by Django 5.1.3 on 2024-12-04 17:05

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_remove_follow_self_subscribe_constraint_and_more'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='follow',
            name='Self subscribe constraint',
        ),
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(max_length=150, validators=[django.core.validators.RegexValidator(message='Имя и Фамилия должны содержать буквенные символыили разрешенные символы `/./- и пробел', regex='^[a-zA-Zа-яА-ЯёЁ\\s\\-\\.\\`]+$')], verbose_name='имя'),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(max_length=150, validators=[django.core.validators.RegexValidator(message='Имя и Фамилия должны содержать буквенные символыили разрешенные символы `/./- и пробел', regex='^[a-zA-Zа-яА-ЯёЁ\\s\\-\\.\\`]+$')], verbose_name='фамилия'),
        ),
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.CheckConstraint(condition=models.Q(('following', models.F('user')), _negated=True), name='Подписка на самого себя'),
        ),
    ]
