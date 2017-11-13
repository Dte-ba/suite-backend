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

distritos = [
  "A. Alsina", "Adolfo Alsina",
  "A. Brown", "Almirante Brown",
  "A. G. Chaves", "Adolfo Gonzales Chaves",
  "B. Juarez", "Benito Juárez",
  "C. Brandsen", "Coronel Brandsen",
  "C. De Areco", "Carmen de Areco",
  "C. Dorrego", "Coronel Dorrego",
  "C. Patagones", "Carmen de Patagones",
  "C. Pringles", "Coronel Pringles",
  "C. Rosales", "Coronel Rosales",
  "C. Sarmiento", "Capitán Sarmiento",
  "C. Suarez", "Coronel Suárez",
  "C. Tejedor", "Carlos Tejedor",
  "E. De La Cruz", "Exaltación de la Cruz",
  "E. Echeverria", "Esteban Echeverría",
  "F. Ameghino", "Florentino Ameghino",
  "G. Alvear", "General Alvear",
  "G. Arenales", "General Arenales",
  "G. Belgrano", "General Belgrano",
  "G. Las Heras", "General Las Heras",
  "G. Lavalle", "General Lavalle",
  "G. Madariaga", "General Madariaga",
  "G. Paz", "General Paz",
  "G. Pinto", "General Pinto",
  "G. Rodriguez", "General Rodríguez",
  "G. Viamonte", "General Viamonte",
  "G. Villegas", "General Villegas",
  "Gral. Alvarado", "General Alvarado",
  "Gral. Pueyrredón", "General Pueyrredón",
  "Gral. San Martín", "General San Martín",
  "Hurlingahm", "Hurlingham",
  "L. N. Alem", "Leandro N. Alem",
  "Lanus", "Lanús",
  "M. Argentinas", "Malvinas Argentinas",
  "M. Hermoso", "Monte Hermoso",
  "Pte. Perón", "Presidente Perón",
  "Roque Perez", "Roque Pérez",
  "S. A. De Giles", "San Antonio de Giles",
  "S. Cayetano", "San Cayetano",
  "San Nicolas", "San Nicolás",
  "T. De Febrero", "Tres de Febrero",
  "T. Lauquen", "Trenque Lauquen",
  "Tapalque", "Tapalqué",
  "Vte. Lopez", "Vicente López",
  "Zarate", "Zárate"
]


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
