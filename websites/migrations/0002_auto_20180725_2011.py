# Generated by Django 2.0.4 on 2018-07-25 20:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('websites', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='site',
            name='status',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='site',
            name='robots',
            field=models.BooleanField(default=False),
        ),
    ]