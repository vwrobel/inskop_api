# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-11-19 11:25
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('scene_manager', '0009_auto_20161119_1115'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='analysis',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                    to='scene_manager.Analysis'),
        ),
    ]