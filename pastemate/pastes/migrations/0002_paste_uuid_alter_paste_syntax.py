# Generated by Django 4.0.5 on 2022-06-03 08:51

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pastes", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="paste",
            name="uuid",
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
        migrations.AlterField(
            model_name="paste",
            name="syntax",
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
