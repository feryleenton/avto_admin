# Generated by Django 3.1.6 on 2021-02-02 00:03

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_auto_20210202_0000'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='lead_time',
            field=models.DateTimeField(default=datetime.datetime(2021, 2, 2, 0, 3, 34, 617585), null=True, verbose_name='время выполнения'),
        ),
    ]
