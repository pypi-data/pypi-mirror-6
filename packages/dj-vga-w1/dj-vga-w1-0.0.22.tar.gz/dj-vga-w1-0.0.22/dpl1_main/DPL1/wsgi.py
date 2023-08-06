"""
WSGI config for DPL1 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
from dpl1_main.deployment_util import correct_sys_path



correct_sys_path('../..')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dpl1_main.DPL1.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
