# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-11-11 16:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('scene_manager', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='analysis',
            name='locked',
            field=models.BooleanField(default=True),
        ),
    ]
