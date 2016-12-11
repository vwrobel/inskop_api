from __future__ import unicode_literals

from autoslug import AutoSlugField
from django.contrib.auth.models import User
from django.db import models


class AuthorizationLevel(models.Model):
    name = models.CharField(max_length=90)
    level = models.IntegerField()
    description = models.CharField(max_length=90, null=True, blank=True)

    def __str__(self):
        return self.name


class Auth0User(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    auth0_id = models.CharField(max_length=90)
    name = models.CharField(max_length=90, blank=True, null=True)
    slug = AutoSlugField(populate_from='name', always_update=True, unique=True)
    email = models.CharField(max_length=90, blank=True, null=True)
    picture = models.CharField(max_length=400, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    authorization = models.ForeignKey(AuthorizationLevel, blank=True, null=True)

    def __str__(self):
        return self.name
