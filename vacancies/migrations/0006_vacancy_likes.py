# Generated by Django 4.1.7 on 2023-03-22 09:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("vacancies", "0005_skill_is_active"),
    ]

    operations = [
        migrations.AddField(
            model_name="vacancy",
            name="likes",
            field=models.IntegerField(default=0),
        ),
    ]
