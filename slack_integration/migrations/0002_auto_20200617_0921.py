# Generated by Django 3.0.7 on 2020-06-17 09:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('slack_integration', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actionsblock',
            name='template',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='actions_block', to='slack_integration.Template'),
        ),
    ]
