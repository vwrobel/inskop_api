# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-11-11 21:27
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('account_manager', '0001_initial'),
        ('scene_manager', '0003_auto_20161111_1634'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='owner',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE,
                                    to='account_manager.Auth0User'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='selection',
            name='name',
            field=models.CharField(default='dummy', max_length=40),
            preserve_default=False,
        ),
    ]