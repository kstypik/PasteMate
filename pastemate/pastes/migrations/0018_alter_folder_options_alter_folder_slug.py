# Generated by Django 4.0.5 on 2022-06-08 17:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pastes", "0017_alter_folder_name_folder_unique_folder_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="folder",
            options={"ordering": ["name"]},
        ),
        migrations.AlterField(
            model_name="folder",
            name="slug",
            field=models.SlugField(),
        ),
    ]
