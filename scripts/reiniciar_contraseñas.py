# coding: utf-8
from __future__ import unicode_literals
import sys
import pprint
import os
import django
import pprint
sys.path.append("..")
sys.path.append(".")
# Configuración inicial de django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "suite.settings")
django.setup()

from escuelas import models
from django.contrib.auth.models import User

password = 'asdasd123'

print "Reiniciando contraseñas..."
print "--------------------------"

for user in User.objects.order_by('username'):
    user.set_password(password)

    if user.is_superuser:
        print "Usuario Administrador:", user
    else:
        print "Usuario", user

    user.save()
