# coding: utf-8
from django_rq import job
import tempfile
import django
import time
import utils
import os
import re
import json
import tempfile
import shutil
import xlwt
import zipfile
import glob

from escuelas import models


@job
def distribuir_paquetes(distribucion_de_paquete):
    trabajo = utils.crear_modelo_trabajo("Distribución de paquetes id={0}".format(distribucion_de_paquete.id))

    try:
        directorio_temporal = tempfile.mkdtemp()
        ruta_del_archivo_de_log = os.path.join(directorio_temporal, "log.txt")
        archivo_log = open(ruta_del_archivo_de_log, "wt")

        trabajo.actualizar_paso(1, 3, 'Comenzando distribucion de paquetes')
        trabajo.actualizar_paso(1, 3, 'Descomprimiendo archivo .zip de educ.ar')

        archivo_zip = zipfile.ZipFile(distribucion_de_paquete.archivo.path)
        archivo_zip.extractall(directorio_temporal)
        archivo_zip.close()

        # Aquí se asume que el archivo tiene un directorio dentro, y ahí todos
        # los archivos .zip
        archivos = glob.glob(os.path.join(directorio_temporal, "*", "*"))
        archivos_zip = [archivo for archivo in archivos if archivo.lower().endswith('.zip')]

        if len(archivos_zip) > 0:
            trabajo.actualizar_paso(2, 3, "Buscando solicitudes de {0} paquetes devueltos".format(len(archivos_zip)))
        else:
            raise Exception("No se buscaran solicitudes porque la devolucion parece vacia.")

        for ruta in archivos_zip:
            nombre = os.path.basename(ruta)
            numero = nombre.lower().replace('.zip', '')
            numero_hex = hex(int(numero)).split('x')[1]

            estado = models.Paquete.cambiar_estado_a_entregado(numero_hex, ruta)

            if estado:
                mensaje = "Cambiando el estado del paquete {0} (hex {1})".format(numero, numero_hex)
            else:
                mensaje = "CUIDADO: no se encontro el paquete {0} (hex {1})".format(numero, numero_hex)

            archivo_log.write(mensaje + "\n")
            trabajo.actualizar_paso(2, 3, mensaje)

        trabajo.actualizar_paso(3, 3, "Finalizado")
        archivo_log.close()

        archivo = open(ruta_del_archivo_de_log, "rt")
        trabajo.archivo.save("resultado.log", django.core.files.base.File(archivo))
        archivo.close()

        trabajo.resultado = json.dumps({'ok': True})
        trabajo.save()
        shutil.rmtree(directorio_temporal)
    except Exception as e:
        trabajo.error = str(e)
        trabajo.save()
        raise Exception(e)

    return trabajo
