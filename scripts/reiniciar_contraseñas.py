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

for user in User.objects.all():
    user.set_password(password)
    print "Reiniciando contraseña de", user, "a", password
    user.save()
