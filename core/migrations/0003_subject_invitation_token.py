# Generated by Django 4.1.5 on 2023-01-28 14:28

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_alter_tasksession_started_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="subject",
            name="invitation_token",
            field=models.CharField(
                default=core.models.generate_invitation_token, max_length=32
            ),
        ),
    ]