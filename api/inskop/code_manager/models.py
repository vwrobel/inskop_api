from __future__ import unicode_literals

import os.path

from autoslug import AutoSlugField
from django.conf import settings
from django.db import models

from ..account_manager.models import Auth0User
from ..storage import OverwriteStorage


class CodeCategory(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


def code_path(instance, filename=''):
    # file will be uploaded to MEDIA_ROOT/...
    return 'codes/{0}/main.py'.format(instance.name)


class Code(models.Model):
    name = models.CharField(max_length=30)
    slug = AutoSlugField(populate_from='name', always_update=True, unique=True)
    owner = models.ForeignKey(Auth0User)
    description = models.CharField(max_length=400, blank=True, null=True)
    category = models.ForeignKey(CodeCategory, on_delete=models.CASCADE, null=True)
    code = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to=code_path, storage=OverwriteStorage(), blank=True, null=True)
    read_me = models.TextField(blank=True, null=True)
    default_param = models.CharField(max_length=400, blank=True, null=True)
    valid = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    locked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_path(self, with_mediaroot=False):
        if with_mediaroot:
            mediaroot = settings.MEDIA_ROOT
        else:
            mediaroot = None
        return os.path.join(mediaroot, code_path(self))

    @property
    def favorite_count(self):
        favorite_code = FavoriteCode.objects.filter(code=self).exclude(user=self.owner)
        favorite_count = len(favorite_code)
        return favorite_count

    def is_user_favorite(self, user):
        user_favorite = FavoriteCode.objects.filter(user=user, code=self)
        return len(user_favorite) > 0

    def is_user_owner(self, user):
        return self.owner == user


class FavoriteCode(models.Model):
    code = models.ForeignKey(Code)
    user = models.ForeignKey(Auth0User)

    def __str__(self):  # __unicode__ on Python 2
        return self.user.name + '_' + self.code.name


class Process(models.Model):
    name = models.CharField(max_length=40)
    slug = AutoSlugField(populate_from='name', always_update=True, unique=True)
    owner = models.ForeignKey(Auth0User)
    process = models.TextField(max_length=1000, blank=True, null=True)
    description = models.CharField(max_length=400, blank=True, null=True)

    def __str__(self):
        return self.name
