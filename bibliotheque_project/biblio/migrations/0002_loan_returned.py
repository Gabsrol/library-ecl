# Generated by Django 3.0.5 on 2020-12-01 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('biblio', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='loan',
            name='returned',
            field=models.BooleanField(default=False),
        ),
    ]
