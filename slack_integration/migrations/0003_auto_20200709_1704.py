# Generated by Django 3.0.8 on 2020-07-09 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('slack_integration', '0002_auto_20200703_0623'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messagetimestamp',
            name='ts',
            field=models.CharField(max_length=20, unique=True),
        ),
    ]
