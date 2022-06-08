# Generated by Django 4.0.5 on 2022-06-08 08:39

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('pastes', '0012_alter_paste_embeddable_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('reason', models.TextField()),
                ('reporter_name', models.CharField(max_length=100)),
                ('pending', models.BooleanField(default=False)),
                ('paste', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pastes.paste')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
