# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-12-12 13:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scene_manager', '0024_auto_20161211_0953'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
