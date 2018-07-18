# Generated by Django 2.0.4 on 2018-06-15 13:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0010_auto_20180606_0615'),
    ]

    operations = [
        migrations.AlterField(
            model_name='replacement',
            name='typos',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='replacements', to='dashboard.TyposGrammar'),
        ),
        migrations.AlterField(
            model_name='site',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sites', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='typosgrammar',
            name='content',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='typosgrammars', to='dashboard.Content'),
        ),
    ]