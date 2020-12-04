# Generated by Django 3.0.5 on 2020-12-03 22:18

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('biblio', '0012_auto_20201203_2318'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bad_borrower',
            name='ending_date',
            field=models.DateField(default=datetime.datetime(2022, 11, 10, 22, 18, 27, 972269, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='loan',
            name='beginning_date',
            field=models.DateField(default=datetime.datetime(2020, 12, 3, 22, 18, 27, 971631, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='loan',
            name='ending_date',
            field=models.DateField(default=datetime.datetime(2021, 1, 2, 22, 18, 27, 971658, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='beginning_date',
            field=models.DateField(default=datetime.datetime(2020, 12, 3, 22, 18, 27, 971028, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='ending_date',
            field=models.DateField(default=datetime.datetime(2021, 12, 2, 22, 18, 27, 971074, tzinfo=utc)),
        ),
    ]
