# Generated by Django 3.0.5 on 2020-12-03 22:18

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('biblio', '0011_auto_20201203_2317'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bad_borrower',
            name='ending_date',
            field=models.DateField(default=datetime.datetime(2022, 11, 10, 22, 18, 20, 410238, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='loan',
            name='beginning_date',
            field=models.DateField(default=datetime.datetime(2020, 12, 3, 22, 18, 20, 409652, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='loan',
            name='ending_date',
            field=models.DateField(default=datetime.datetime(2021, 1, 2, 22, 18, 20, 409679, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='beginning_date',
            field=models.DateField(default=datetime.datetime(2020, 12, 3, 22, 18, 20, 409000, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='ending_date',
            field=models.DateField(default=datetime.datetime(2021, 12, 2, 22, 18, 20, 409052, tzinfo=utc)),
        ),
    ]
