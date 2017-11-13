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


def eliminar_duplicados(solo_simular, verbose):

    def log(mensaje):
        if verbose:
            print(mensaje)

    log("Intentando encontrar y eliminar duplicados")

    if solo_simular:
        log("Modo simulación, no se eliminaran registros")
    else:
        log("Modo real: se eliminaran efectivamente los registros")

if __name__ == "__main__":
    eliminar_duplicados(solo_simular=False, verbose=True)
