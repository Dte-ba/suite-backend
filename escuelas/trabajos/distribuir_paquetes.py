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
        # los archivos .zip (uno por cada cue) y directorios por cada uno de
        # los cue.
        archivos = glob.glob(os.path.join(directorio_temporal, "*", "*"))
        directorios = [archivo for archivo in archivos if os.path.isdir(archivo)]
        archivos_de_paquetes = glob.glob(os.path.join(directorio_temporal, "*", "*", "*"))
        paquetes_bin = [paquete for paquete in archivos_de_paquetes if paquete.endswith("bin")]
        paquetes_min = [paquete for paquete in archivos_de_paquetes if paquete.endswith("min")]

        if len(directorios) > 0:
            trabajo.actualizar_paso(2, 3, "Buscando solicitudes de {0} cue paquetes devueltos".format(len(paquetes_bin)))
        else:
            raise Exception("No se buscaran solicitudes porque la devolucion parece vacia.")

        for ruta in paquetes_bin:
            nombre = os.path.basename(ruta)
            regex = re.search('tcopp_(.*)_(.*)\.bin', os.path.basename(ruta))

            if regex:
                (id_hardware, marca_de_arranque_hex) = regex.groups()

                mensaje = models.Paquete.cambiar_estado_a_entregado(id_hardware, marca_de_arranque_hex, ruta)
            else:
                mensaje = "CUIDADO: ignorando el archivo {0} porque no coincide con el formato de paquete esperado (tcopp_idhardware_ma.bin)"

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
