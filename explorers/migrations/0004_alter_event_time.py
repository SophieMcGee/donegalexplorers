# Generated by Django 4.2.15 on 2024-08-28 04:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('explorers', '0003_rating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='time',
            field=models.TimeField(),
        ),
    ]
