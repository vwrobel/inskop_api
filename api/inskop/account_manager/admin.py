from django.contrib import admin

from ..account_manager.models import Auth0User, AuthorizationLevel

# Register your models here.
model_list = [Auth0User, AuthorizationLevel]
admin.site.register(model_list)
