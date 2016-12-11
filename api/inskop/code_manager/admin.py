from django.contrib import admin

from ..code_manager.models import Process, Code, CodeCategory

# Register your models here.
model_list = [Process, Code, CodeCategory]  # iterable list
admin.site.register(model_list)
