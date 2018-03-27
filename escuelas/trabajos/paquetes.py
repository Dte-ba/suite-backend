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


from easy_pdf.rendering import render_to_pdf
from django.template import loader
from escuelas import models


FORMATO_FECHA = "\d{4}-\d{2}-\d{2}"

def formatear_fecha(fecha_como_string):
    import datetime
    return datetime.datetime.strptime(fecha_como_string, "%Y-%m-%d").strftime("%d/%m/%Y")

@job
def exportar_paquetes(inicio, fin, estadoPedido):
    trabajo = utils.crear_modelo_trabajo("Exportación de paquetes de estado {0} completo desde {1} hasta {2}".format(estadoPedido, inicio, fin))

    directorio_temporal = tempfile.mkdtemp()
    directorio_del_archivo_zip = tempfile.mkdtemp()

    trabajo.actualizar_paso(1, 3, "Solicitando paquetes")

    data = models.Paquete.obtener_paquetes_para_exportar(inicio, fin, estadoPedido)
    llaves = data['llaves']
    data['llaves'] = [str(llave) for llave in data['llaves']]

    # copia las llaves al directorio temporal que se comprimirá
    for llave in llaves:
        trabajo.actualizar_paso(1, 3, "Copiando llave {0}".format(llave.name))
        shutil.copy(llave.path, directorio_temporal)

    # Genera un archivo .zip del directorio temporal con todas las llaves
    nombre_del_archivo_zip = u'exportacion_de_paquetes_desde_{0}_hasta_{1}'.format(inicio, fin)
    ruta_del_archivo_zip = os.path.join(directorio_del_archivo_zip, nombre_del_archivo_zip)
    shutil.make_archive(ruta_del_archivo_zip, 'zip', directorio_temporal)

    # Guarda el .zip como un archivo django para preservarlo en el trabajo.
    archivo = open(ruta_del_archivo_zip + ".zip")
    trabajo.archivo.save(u"exportacion_de_paquetes_{0}_hasta_{1}".format(inicio, fin), django.core.files.base.File(archivo))
    archivo.close()

    trabajo.resultado = json.dumps({'data': data})
    trabajo.save()

    trabajo.actualizar_paso(2, 3, "Generando archivos comprimido")

    trabajo.actualizar_paso(3, 3, "Finalizado")


    # Elimina los directorios temporales (y el .zip temporal)
    shutil.rmtree(directorio_temporal)
    shutil.rmtree(directorio_del_archivo_zip)
    return trabajo


def ____________tmp_____________generar_informe_de_region(numero_de_region, desde, hasta):
    trabajo = utils.crear_modelo_trabajo("Informe de region {0} completo desde {1} hasta {2}".format(numero_de_region, desde, hasta))

    directorio_temporal = tempfile.mkdtemp()
    directorio_del_archivo_zip = tempfile.mkdtemp()

    region = models.Region.objects.get(numero=numero_de_region)
    cantidad_de_pasos = region.perfiles.count() + 2
    trabajo.actualizar_paso(1, cantidad_de_pasos, "Solicitando perfiles")

    # Genera un archivo pdf por cada perfil.
    for (numero, perfil) in enumerate(region.perfiles.filter(fecha_de_renuncia=None)):
        trabajo.actualizar_paso(1 + numero, cantidad_de_pasos, u"Obteniendo informe de {0} {1}".format(perfil.apellido, perfil.nombre))
        nombre_del_archivo = u"informe_de_{0}".format(perfil.nombre)
        ruta = os.path.join(directorio_temporal, obtener_nombre_de_archivo_informe(perfil))
        crear_informe_en_archivo_pdf(ruta, perfil, desde, hasta)

    trabajo.actualizar_paso(cantidad_de_pasos, cantidad_de_pasos, u"Generando archivo .zip para descargar")

    # Genera un archivo .zip con todos los informes
    nombre_del_archivo_zip = u'informes_region_{0}'.format(numero_de_region)
    ruta_del_archivo_zip = os.path.join(directorio_del_archivo_zip, nombre_del_archivo_zip)
    shutil.make_archive(ruta_del_archivo_zip, 'zip', directorio_temporal)

    # Guarda el .zip como un archivo django para preservarlo en el trabajo.
    archivo = open(ruta_del_archivo_zip + ".zip")
    trabajo.archivo.save(u"informe_de_la_region_{0}.zip".format(region.numero), django.core.files.base.File(archivo))
    archivo.close()
    trabajo.resultado = json.dumps({'region': region.numero})
    trabajo.save()

    # Elimina los directorios temporales (y el .zip temporal)
    shutil.rmtree(directorio_temporal)
    shutil.rmtree(directorio_del_archivo_zip)
    return trabajo
