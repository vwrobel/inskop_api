from django.contrib import admin

from jobs.models import Job

# Register your models here.
model_list = [Job]  # iterable list
admin.site.register(model_list)