# Generated by Django 2.0.4 on 2018-05-16 19:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_auto_20180516_1834'),
    ]

    operations = [
        migrations.AlterField(
            model_name='content',
            name='path',
            field=models.CharField(max_length=100),
        ),
    ]