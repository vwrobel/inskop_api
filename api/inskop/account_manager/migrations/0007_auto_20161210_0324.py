# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-12-10 03:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account_manager', '0006_auth0user_staff'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuthorizationLevel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=90)),
                ('level', models.IntegerField()),
                ('description', models.CharField(blank=True, max_length=90, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='auth0user',
            name='staff',
        ),
        migrations.AddField(
            model_name='auth0user',
            name='authorization',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='account_manager.AuthorizationLevel'),
        ),
    ]