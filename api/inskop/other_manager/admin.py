from django.contrib import admin

from ..other_manager.models import Doc

# Register your models here.
model_list = [Doc]  # iterable list
admin.site.register(model_list)
