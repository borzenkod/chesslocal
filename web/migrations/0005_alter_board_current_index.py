# Generated by Django 5.0.1 on 2024-01-22 10:48

import web.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0004_alter_variant_main_line'),
    ]

    operations = [
        migrations.AlterField(
            model_name='board',
            name='current_index',
            field=models.JSONField(default=web.models.Board.dciv),
        ),
    ]
