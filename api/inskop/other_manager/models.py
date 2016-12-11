from __future__ import unicode_literals

from autoslug import AutoSlugField
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from ..storage import OverwriteStorage

_UNSAVED_FILEFIELD = 'unsaved_filefield'


def doc_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/...
    return 'docs/{0}/doc.pdf'.format(instance.slug)


class Doc(models.Model):
    title = models.CharField(max_length=30)
    file = models.FileField(upload_to=doc_path, storage=OverwriteStorage(), blank=True, null=True)
    active = models.BooleanField(default=True)
    slug = AutoSlugField(populate_from='title')

    def __str__(self):
        return self.slug


@receiver(pre_save, sender=Doc)
def skip_saving_file(sender, instance, **kwargs):
    if not instance.pk and not hasattr(instance, _UNSAVED_FILEFIELD):
        setattr(instance, _UNSAVED_FILEFIELD, instance.file)
        instance.file = None


@receiver(post_save, sender=Doc)
def save_file(sender, instance, created, **kwargs):
    if created and hasattr(instance, _UNSAVED_FILEFIELD):
        instance.file = getattr(instance, _UNSAVED_FILEFIELD)
        instance.save()
        instance.__dict__.pop(_UNSAVED_FILEFIELD)
