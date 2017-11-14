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

mapa_de_distritos = {
  "A. Alsina": "Adolfo Alsina",
  "A. Brown": "Almirante Brown",
  "A. G. Chaves": "Adolfo Gonzales Chaves",
  "B. Juarez": "Benito Juárez",
  "C. Brandsen": "Coronel Brandsen",
  "C. De Areco": "Carmen de Areco",
  "C. Dorrego": "Coronel Dorrego",
  "C. Patagones": "Carmen de Patagones",
  "C. Pringles": "Coronel Pringles",
  "C. Rosales": "Coronel Rosales",
  "C. Sarmiento": "Capitán Sarmiento",
  "C. Suarez": "Coronel Suárez",
  "C. Tejedor": "Carlos Tejedor",
  "E. De La Cruz": "Exaltación de la Cruz",
  "E. Echeverria": "Esteban Echeverría",
  "F. Ameghino": "Florentino Ameghino",
  "G. Alvear": "General Alvear",
  "G. Arenales": "General Arenales",
  "G. Belgrano": "General Belgrano",
  "G. Las Heras": "General Las Heras",
  "G. Lavalle": "General Lavalle",
  "G. Madariaga": "General Madariaga",
  "G. Paz": "General Paz",
  "G. Pinto": "General Pinto",
  "G. Rodriguez": "General Rodríguez",
  "G. Viamonte": "General Viamonte",
  "G. Villegas": "General Villegas",
  "Gral. Alvarado": "General Alvarado",
  "Gral. Pueyrredón": "General Pueyrredón",
  "Gral. San Martín": "General San Martín",
  "Hurlingahm": "Hurlingham",
  "L. N. Alem": "Leandro N. Alem",
  "Lanus": "Lanús",
  "M. Argentinas": "Malvinas Argentinas",
  "M. Hermoso": "Monte Hermoso",
  "Pte. Perón": "Presidente Perón",
  "Roque Perez": "Roque Pérez",
  "S. A. De Giles": "San Antonio de Giles",
  "S. Cayetano": "San Cayetano",
  "San Nicolas": "San Nicolás",
  "T. De Febrero": "Tres de Febrero",
  "T. Lauquen": "Trenque Lauquen",
  "Tapalque": "Tapalqué",
  "Vte. Lopez": "Vicente López",
  "Zarate": "Zárate"
}


def eliminar_duplicados(solo_simular, verbose):

    def log(mensaje):
        if verbose:
            print(mensaje)

    if solo_simular:
        log("Modo simulación, no se eliminaran registros")
    else:
        log("Modo real: se eliminaran efectivamente los registros")

    log("Unificando nombres de distritos")
    todos_los_distritos = models.Distrito.objects.order_by('id').all()

    log(" Hay %d distritos (deberían quedar 138 al final)" %(len(todos_los_distritos)))

    for distrito in todos_los_distritos:

        if distrito.nombre in mapa_de_distritos:
            log("  El distrito id=%d en realidad tiene mal el nombre" %(distrito.id))

            if not solo_simular:
                distrito.nombre = mapa_de_distritos[distrito.nombre]
                distrito.save()
                log("  Corrigiendo nombre al distrito %s (id=%d)" %(distrito.nombre, distrito.id))

    log("Buscando duplicados de distritos")

    nombres_unicos = set([d.nombre for d in todos_los_distritos])

    log(" Hay %d distritos unicos, el resto son duplicados" %(len(nombres_unicos)))

    for x in nombres_unicos:
        distritos_duplicados = models.Distrito.objects.filter(nombre=x)
        cantidad_repeticiones = len(distritos_duplicados)

        if cantidad_repeticiones > 1:
            log("  Hay %d registros duplicados para el distrito %s" %(cantidad_repeticiones -1, x))

            distrito_a_preservar = distritos_duplicados[0]
            distritos_a_eliminar = distritos_duplicados[1:]

            for distrito_a_eliminar in distritos_a_eliminar:

                if not solo_simular:
                    [distrito_a_preservar.localidades.add(d) for d in distrito_a_eliminar.localidades.all()]
                    distrito_a_preservar.save()
                    distrito_a_eliminar.save()
                    log("   Eliminando el distrito %s (id=%d) luego de haber re-asignado localidades" %(distrito_a_eliminar.nombre, distrito_a_eliminar.id))
                    distrito_a_eliminar.delete()


    log("Buscando distritos sin vincular a regiones")

    distritos_sin_region = models.Distrito.objects.filter(region=None)

    if distritos_sin_region:
        log("Hay %d distritos sin región" %(distritos_sin_region.count()))
    else:
        log("No hay distritos sin región")


    log("Buscando localidades para unificar")
    todos_los_distritos = models.Distrito.objects.order_by('id').all()

    for distrito in todos_los_distritos:
        log(" Buscando unificar localidades del distrito %s" %(distrito.nombre))
        localidades_del_distrito = distrito.localidades.all()
        cantidad_de_localidades_en_el_distrito = len(localidades_del_distrito)

        nombres_unicos_de_localides = set([l.nombre for l in localidades_del_distrito])
        cantidad_unicos = len(nombres_unicos_de_localides)

        log("  Hay %d distritos unicos, %d son duplicados" %(cantidad_unicos, cantidad_de_localidades_en_el_distrito - cantidad_unicos))

        


    #for distrito in distritos_sin_region:


if __name__ == "__main__":
    eliminar_duplicados(solo_simular=False, verbose=True)
