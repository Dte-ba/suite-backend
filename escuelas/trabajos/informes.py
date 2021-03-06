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
from escuelas import models


FORMATO_FECHA = "\d{4}-\d{2}-\d{2}"

def formatear_fecha(fecha_como_string):
    import datetime
    return datetime.datetime.strptime(fecha_como_string, "%Y-%m-%d").strftime("%d/%m/%Y")

@job
def generar_informe_de_region(numero_de_region, desde, hasta, aplicacion):
    trabajo = utils.crear_modelo_trabajo("Informe de region {0} completo desde {1} hasta {2}".format(numero_de_region, desde, hasta))

    directorio_temporal = tempfile.mkdtemp()
    directorio_del_archivo_zip = tempfile.mkdtemp()

    region = models.Region.objects.get(numero=numero_de_region)
    cantidad_de_pasos = region.perfiles.count() + 2
    trabajo.actualizar_paso(1, cantidad_de_pasos, "Solicitando perfiles con acceso a {}".format(aplicacion))

    try:
        objeto_aplicacion = models.Aplicacion.objects.get(identificador=aplicacion)
    except models.Aplicacion.DoesNotExist:
        trabajo.error = "No se encuentra ese tipo de aplicacion: {}.".format(aplicacion)
        trabajo.save()
        return

    # Genera un archivo pdf por cada perfil.
    for (numero, perfil) in enumerate(region.perfiles.filter(fecha_de_renuncia=None , aplicaciones=objeto_aplicacion)):
        trabajo.actualizar_paso(1 + numero, cantidad_de_pasos, u"Obteniendo informe de {0} {1}".format(perfil.apellido, perfil.nombre))
        nombre_del_archivo = u"informe_de_{0}".format(perfil.nombre)
        ruta = os.path.join(directorio_temporal, obtener_nombre_de_archivo_informe(perfil))
        crear_informe_en_archivo_pdf(ruta, perfil, desde, hasta, aplicacion)

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

def crear_informe_en_archivo_pdf(ruta, perfil, desde, hasta, aplicacion):
    if aplicacion == 'suite':
        eventos = perfil.obtener_eventos_por_fecha(desde, hasta)
    else:
        eventos = perfil.obtener_eventos_de_robotica_por_fecha(desde, hasta)

    contexto = {
        "perfil": perfil,
        "eventos": eventos,
        "desde": formatear_fecha(desde),
        "hasta": formatear_fecha(hasta),
    }

    if aplicacion == 'suite':
        contenido = render_to_pdf("informe.html", contexto)
    else:
        contenido = render_to_pdf("informe_robotica.html", contexto)

    archivo2 = open(ruta, "w")
    archivo2.write(contenido)
    archivo2.close()

def obtener_nombre_de_archivo_informe(perfil):
    if perfil.cargo:
        cargo = perfil.cargo.nombre
    else:
        cargo = "sin_cargo"
    return u'informe_region_{0}_{1}_{2}_{3}.pdf'.format(perfil.region.numero, cargo, perfil.apellido, perfil.nombre)

@job
def generar_informe_de_perfil(perfil_id, desde, hasta, aplicacion):
    trabajo = utils.crear_modelo_trabajo("Informe de perfil {0} desde {1} hasta {2}".format(perfil_id, desde, hasta))

    if None in [perfil_id, desde, hasta, aplicacion]:
        trabajo.error = "No han especificado todos los argumentos: perfil_id, desde y hasta."
        trabajo.save()
        return

    try:
        objeto_aplicacion = models.Aplicacion.objects.get(identificador=aplicacion)
    except models.Aplicacion.DoesNotExist:
        trabajo.error = "No se encuentra ese tipo de aplicacion."
        trabajo.save()
        return

    if not re.match(FORMATO_FECHA, desde) or not re.match(FORMATO_FECHA, hasta):
        trabajo.error = "Las fechas están en formato incorrecto, deben ser YYYY-MM-DD."
        trabajo.save()
        return

    trabajo.actualizar_paso(1, 4, "Solicitando datos desde {0} hasta {1}".format(desde, hasta))

    perfil = models.Perfil.objects.get(id=perfil_id)

    if aplicacion == 'suite':
        eventos = perfil.obtener_eventos_por_fecha(desde, hasta)
    elif aplicacion == 'robotica':
        eventos = perfil.obtener_eventos_de_robotica_por_fecha(desde, hasta)
    else:
        trabajo.error = "No se pueden filtrar los eventos para la aplicacion {}.".format(aplicacion)
        trabajo.save()
        return

    trabajo.actualizar_paso(1, 4, "Procesando {0} eventos".format(len(eventos)))

    trabajo.actualizar_paso(2, 4, "Generando archivo")
    trabajo.resultado = json.dumps({'perfil_id': perfil_id, 'cantidad_de_eventos': len(eventos)})

    contexto = {
        "perfil": perfil,
        "eventos": eventos,
        "desde": formatear_fecha(desde),
        "hasta": formatear_fecha(hasta),
    }

    if aplicacion == 'suite':
        contenido = render_to_pdf("informe.html", contexto)
    else:
        contenido = render_to_pdf("informe_robotica.html", contexto)

    archivo =  django.core.files.base.ContentFile(contenido)
    trabajo.archivo.save(obtener_nombre_de_archivo_informe(perfil), archivo)

    trabajo.actualizar_paso(4, 4, "Finalizando")
    trabajo.save()
    return trabajo
