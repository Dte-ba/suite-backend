# coding: utf-8
import sys
import pprint
import os
import django
import codecs
import re

from utils import log

sys.path.append("..")
sys.path.append(".")

# Configuración inicial de django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "suite.settings")
django.setup()

from escuelas import models

ARCHIVO = "archivos_para_importacion/regiones.txt"

log("iniciando la importación del archivo: " + ARCHIVO)
archivo = codecs.open(ARCHIVO, "r", "utf-8")

def obtener_numero_de_region(linea):
    busqueda = re.search('Region (.*)', linea, re.IGNORECASE)
    return busqueda.group(1)

def obtener_region(linea):
    busqueda = re.search('\[(.*)\] (.*)', linea, re.IGNORECASE)
    nombre = busqueda.group(2)
    es_cabecera = False

    if nombre.endswith("*"):
        es_cabecera = True
        nombre = nombre[:-1]

    return {
        "numero": busqueda.group(1),
        "nombre": nombre,
        "esCabecera": es_cabecera
    }

def buscar_u_obtener_registro_de_region(numero_de_region):
    resultado = models.Region.objects.get_or_create(numero=numero_de_region)

    if resultado[1]:
        log("Creando region nro " + numero_de_region)

    return resultado[0]

def buscar_u_obtener_registro_de_municipio(datos_del_municipio, registro_de_region_a_la_que_pertenece):
    resultado = models.Municipio.objects.get_or_create(
        numero = datos_del_municipio['numero'],
        nombre = datos_del_municipio['nombre'],
        esCabecera = datos_del_municipio['esCabecera'],
        region=registro_de_region_a_la_que_pertenece
    )

    if resultado[1]:
        log("Creando el municipio de nombre " + datos_del_municipio['nombre'])
    else:
        log("Actualizando el municipio de nombre " + datos_del_municipio['nombre'])

    return resultado[0]


def main():
    linea_region = None
    registro_region = None

    for linea in archivo:

        if linea.startswith("Region"):
            linea_region = obtener_numero_de_region(linea)
            registro_region = buscar_u_obtener_registro_de_region(linea_region)
            continue

        if linea.startswith("["):
            municipio = obtener_region(linea)
            buscar_u_obtener_registro_de_municipio(municipio, registro_region)
            #print "REGION NRO: ", linea_region, municipio

    archivo.close()


if __name__ == "__main__":
    main()
