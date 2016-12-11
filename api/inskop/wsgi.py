"""
WSGI config for inskop project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

from os.path import join, dirname, exists
from dotenv import load_dotenv

dotenv_path = join(dirname(dirname(__file__)), '.env')
if exists(dotenv_path):
    load_dotenv(dotenv_path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "inskop.settings")

application = get_wsgi_application()
