# Generated by Django 3.1.6 on 2021-02-01 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_remove_service_time_slot'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='time_slot',
            field=models.CharField(choices=[(1, '9:30 - 10:00'), (2, '13:00 - 13:30'), (3, '14:00 - 14:30'), (4, '15:00 - 15:30'), (5, '16:00 - 16:30'), (6, '17:00 - 17:30'), (7, '18:00 - 18:30'), (8, '19:00 - 19:30'), (9, '20:00 - 20:30')], max_length=25, null=True, verbose_name='Время'),
        ),
    ]
