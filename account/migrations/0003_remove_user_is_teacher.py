# Generated by Django 4.1.5 on 2023-04-30 12:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0002_user_is_teacher"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="is_teacher",
        ),
    ]