# Generated by Django 2.0.4 on 2018-07-28 08:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('websites', '0002_auto_20180725_2011'),
    ]

    operations = [
        migrations.RenameField(
            model_name='site',
            old_name='status',
            new_name='task_status',
        ),
        migrations.AddField(
            model_name='site',
            name='periodic_status',
            field=models.BooleanField(default=False),
        ),
    ]