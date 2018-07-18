# Generated by Django 2.0.4 on 2018-04-26 05:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_auth', '0002_signupcode'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_verified',
            field=models.BooleanField(default=False, help_text='Designates whether this user has completed the email verification process to allow login.', verbose_name='verified'),
        ),
    ]
