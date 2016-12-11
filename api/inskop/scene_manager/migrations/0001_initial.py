# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-11-07 23:01
from __future__ import unicode_literals

import autoslug.fields
import django.db.models.deletion
from django.db import migrations, models

import inskop.scene_manager.models
import inskop.storage


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('account_manager', '0001_initial'),
        ('code_manager', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Analysis',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=40, null=True)),
                ('description', models.CharField(blank=True, max_length=400, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Camera',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField()),
                ('description', models.CharField(blank=True, max_length=400, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='FavoriteScene',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Scene',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('slug', autoslug.fields.AutoSlugField(editable=False, populate_from='name')),
                ('subtitle', models.CharField(blank=True, max_length=100, null=True)),
                ('description', models.CharField(blank=True, max_length=400, null=True)),
                ('date', models.DateTimeField(blank=True, null=True)),
                ('location', models.CharField(blank=True, max_length=400, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('locked', models.BooleanField(default=True)),
                ('active', models.BooleanField(default=True)),
                ('valid', models.BooleanField(default=True)),
                ('filters', models.ManyToManyField(blank=True, to='code_manager.Process')),
                ('owner',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account_manager.Auth0User')),
            ],
        ),
        migrations.CreateModel(
            name='SearchZone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('json_item', models.CharField(blank=True, max_length=400, null=True)),
                ('camera', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scene_manager.Camera')),
            ],
        ),
        migrations.CreateModel(
            name='SearchZoneType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
            ],
        ),
        migrations.CreateModel(
            name='Selection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=40, null=True)),
                ('analysis',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scene_manager.Analysis')),
            ],
        ),
        migrations.CreateModel(
            name='SelectionType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='TagCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='TagTarget',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(null=True, storage=inskop.storage.OverwriteStorage(),
                                          upload_to=inskop.scene_manager.models.video_path)),
                ('camera', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scene_manager.Camera')),
                ('filter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='code_manager.Process')),
            ],
        ),
        migrations.CreateModel(
            name='Window',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('t', models.IntegerField()),
                ('json_item', models.CharField(blank=True, max_length=400, null=True)),
                ('camera', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scene_manager.Camera')),
                ('selection',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scene_manager.Selection')),
            ],
        ),
        migrations.CreateModel(
            name='WindowType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
            ],
        ),
        migrations.AddField(
            model_name='window',
            name='type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                    to='scene_manager.WindowType'),
        ),
        migrations.AddField(
            model_name='tagcategory',
            name='target',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scene_manager.TagTarget'),
        ),
        migrations.AddField(
            model_name='tag',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scene_manager.TagCategory'),
        ),
        migrations.AddField(
            model_name='selection',
            name='tags',
            field=models.ManyToManyField(blank=True, to='scene_manager.Tag'),
        ),
        migrations.AddField(
            model_name='selection',
            name='type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                    to='scene_manager.SelectionType'),
        ),
        migrations.AddField(
            model_name='searchzone',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scene_manager.SearchZoneType'),
        ),
        migrations.AddField(
            model_name='scene',
            name='tags',
            field=models.ManyToManyField(blank=True, to='scene_manager.Tag'),
        ),
        migrations.AddField(
            model_name='favoritescene',
            name='scene',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scene_manager.Scene'),
        ),
        migrations.AddField(
            model_name='favoritescene',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account_manager.Auth0User'),
        ),
        migrations.AddField(
            model_name='camera',
            name='scene',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scene_manager.Scene'),
        ),
        migrations.AddField(
            model_name='analysis',
            name='scene',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scene_manager.Scene'),
        ),
        migrations.AddField(
            model_name='analysis',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account_manager.Auth0User'),
        ),
    ]
