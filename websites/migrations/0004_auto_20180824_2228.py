# Generated by Django 2.0.4 on 2018-08-24 22:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('websites', '0003_auto_20180824_2152'),
    ]

    operations = [
        migrations.RenameField(
            model_name='site',
            old_name='user',
            new_name='users',
        ),
    ]