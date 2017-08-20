from __future__ import unicode_literals

from django.apps import AppConfig
from django.db.models.signals import post_migrate

class PermisosConfig(AppConfig):
    name = 'permisos'

    def ready(self):
        uid = "django.contrib.auth.management.create_permissions"
        post_migrate.disconnect(dispatch_uid=uid)
