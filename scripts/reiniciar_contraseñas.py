# coding: utf-8
from __future__ import unicode_literals
import progressbar
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

bar = progressbar.ProgressBar()

for user in bar(User.objects.order_by('username')):
    user.set_password(password)
    user.save()
