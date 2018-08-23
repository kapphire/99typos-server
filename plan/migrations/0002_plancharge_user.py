# Generated by Django 2.0.4 on 2018-08-08 18:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('plan', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='plancharge',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='plans', to=settings.AUTH_USER_MODEL),
        ),
    ]