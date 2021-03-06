# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-11-07 23:01
from __future__ import unicode_literals

import autoslug.fields
from django.db import migrations, models

import inskop.other_manager.models
import inskop.storage


class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Doc',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=30)),
                ('file', models.FileField(blank=True, null=True, storage=inskop.storage.OverwriteStorage(),
                                          upload_to=inskop.other_manager.models.doc_path)),
                ('slug', autoslug.fields.AutoSlugField(editable=False, populate_from='title')),
            ],
        ),
    ]
