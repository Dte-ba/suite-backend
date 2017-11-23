# coding: utf-8
from __future__ import unicode_literals
import sys
import os
import django
sys.path.append("..")
sys.path.append(".")
# Configuración inicial de django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "suite.settings")
django.setup()

from escuelas import models
from django.contrib.auth.models import User

log = None



def eliminar_duplicados(solo_simular, verbose):
    global log

    def imprimir_mensaje(mensaje):
        print(mensaje)

    def omitir_mensaje(mensaje):
        pass

    if verbose:
        log = imprimir_mensaje
    else:
        log = omitir_mensaje

    if solo_simular:
        log("Modo simulación, no se eliminaran registros")
    else:
        log("Modo real: se eliminaran efectivamente los registros")


    unificar_nombres_de_distritos(solo_simular, verbose)
    eliminar_distritos_duplicados(solo_simular, verbose)
    eliminar_distritos_sin_region(solo_simular, verbose)
    eliminar_localidades_duplicadas(solo_simular, verbose)




def unificar_nombres_de_distritos(solo_simular, verbose):
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


def eliminar_distritos_duplicados(solo_simular, verbose):
    log("Buscando duplicados de distritos")

    todos_los_distritos = models.Distrito.objects.order_by('id').all()
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

def eliminar_distritos_sin_region(solo_simular, verbose):
    log("Buscando distritos sin vincular a regiones")

    distritos_sin_region = models.Distrito.objects.filter(region=None)

    if distritos_sin_region:
        log("Hay %d distritos sin región" %(distritos_sin_region.count()))
    else:
        log("No hay distritos sin región")


def eliminar_localidades_duplicadas(solo_simular, verbose):
    log("Buscando localidades para unificar")
    todos_los_distritos = models.Distrito.objects.order_by('id').all()

    for distrito in todos_los_distritos:
        localidades_del_distrito = distrito.localidades.all()
        cantidad_de_localidades_en_el_distrito = len(localidades_del_distrito)

        nombres_unicos_de_localidades = set([l.nombre for l in localidades_del_distrito])
        cantidad_unicos = len(nombres_unicos_de_localidades)

        cantidad_a_eliminar = cantidad_de_localidades_en_el_distrito - cantidad_unicos


        if cantidad_a_eliminar > 0:
            log("  Hay %d localidades, se deben eliminar %d porque son duplicadas." %(cantidad_de_localidades_en_el_distrito, cantidad_a_eliminar))

            for nombre_de_localidad_a_preservar in nombres_unicos_de_localidades:
                localidades_duplicadas = localidades_del_distrito.filter(nombre=nombre_de_localidad_a_preservar)

                if len(localidades_duplicadas) > 1:
                    localidad_a_preservar = localidades_duplicadas[0]
                    log("Se preservará la localidad %s (id: %d)" %(localidad_a_preservar.nombre, localidad_a_preservar.id))

                    localidades_a_eliminar = localidades_duplicadas[1:]

                    for localidad in localidades_a_eliminar:
                        log("  Buscando mover escuelas y perfiles de la localidad duplicada %s (id: %d)" %(localidad.nombre, localidad.id))

                        escuelas = localidad.escuelas.all()

                        if escuelas:
                            for escuela in escuelas:
                                log("     Moviendo la escuela de cue %s (id: %d) a la localidad a preservar (id: %d)" %(escuela.cue, escuela.id, localidad_a_preservar.id))

                                if not solo_simular:
                                    escuela.localidad = localidad_a_preservar
                                    escuela.save()
                        else:
                            log("    No tiene escuelas")

                        perfiles = localidad.perfiles.all()

                        if perfiles:
                            for perfil in perfiles:
                                log("    Moviendo el perfil dni %s (id: %d) a la localidad a preservar (id: %d)" %(perfil.dni, perfil.id, localidad_a_preservar.id))

                                if not solo_simular:
                                    perfil.localidad = localidad_a_preservar
                                    perfil.save()

                        if not solo_simular:
                            log("  Eliminando la localidad duplicada %s (id: %d)" %(localidad.nombre, localidad.id))
                            localidad.delete()

if __name__ == "__main__":
    eliminar_duplicados(solo_simular=False, verbose=True)
