# Generated by Django 3.0.5 on 2020-12-03 22:27

import datetime
from django.db import migrations, models
import django.utils.timezone
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('biblio', '0015_auto_20201203_2324'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bad_borrower',
            name='ending_date',
            field=models.DateField(default=datetime.datetime(2022, 11, 10, 22, 27, 26, 696392, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='loan',
            name='beginning_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='loan',
            name='ending_date',
            field=models.DateField(default=datetime.datetime(2021, 1, 2, 22, 27, 26, 695641, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='ending_date',
            field=models.DateField(default=datetime.datetime(2021, 12, 2, 22, 27, 26, 694975, tzinfo=utc)),
        ),
    ]
