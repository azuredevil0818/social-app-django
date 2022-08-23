# Generated by Django 1.10.7 on 2017-06-08 06:54

from django.db import migrations, models
from django.utils import timezone


class Migration(migrations.Migration):
    dependencies = [
        ('social_django', '0006_partial'),
    ]

    operations = [
        migrations.AddField(
            model_name='code',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True,
                                       db_index=True,
                                       default=timezone.now),
            preserve_default=False
        ),
    ]
