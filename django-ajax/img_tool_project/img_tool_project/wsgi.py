"""
WSGI config for img_tool_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from img_tool_app.models import User

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'img_tool_project.settings')

application = get_wsgi_application()

#apperently adding things to here makes it work only once ..

