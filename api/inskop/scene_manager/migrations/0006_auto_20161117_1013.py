# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-11-17 10:13
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('scene_manager', '0005_remove_scene_filters'),
    ]

    operations = [
        migrations.RenameField(
            model_name='video',
            old_name='filter',
            new_name='process',
        ),
        migrations.AddField(
            model_name='video',
            name='analysis',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE,
                                    to='scene_manager.Analysis'),
        ),
        migrations.AddField(
            model_name='video',
            name='name',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
    ]
