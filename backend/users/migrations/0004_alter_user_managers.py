# Generated by Django 5.1.3 on 2024-11-20 12:01

import users.managers
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_initial'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', users.managers.UserManager()),
            ],
        ),
    ]