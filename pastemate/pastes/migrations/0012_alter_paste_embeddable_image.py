# Generated by Django 4.0.5 on 2022-06-07 06:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pastes", "0011_paste_embeddable_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="paste",
            name="embeddable_image",
            field=models.ImageField(blank=True, upload_to="embed/"),
        ),
    ]
