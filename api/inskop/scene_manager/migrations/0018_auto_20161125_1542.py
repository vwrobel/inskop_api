# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-11-25 15:42
from __future__ import unicode_literals

import autoslug.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('scene_manager', '0017_auto_20161125_1541'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='slug',
            field=autoslug.fields.AutoSlugField(always_update=True, editable=False, populate_from='process',
                                                unique_with=('analysis',)),
        ),
    ]
