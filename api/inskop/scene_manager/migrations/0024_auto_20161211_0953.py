# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-12-11 09:53
from __future__ import unicode_literals

import autoslug.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scene_manager', '0023_auto_20161208_2019'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='slug',
            field=autoslug.fields.AutoSlugField(always_update=True, editable=False, populate_from='name', unique_with=('camera',)),
        ),
    ]
