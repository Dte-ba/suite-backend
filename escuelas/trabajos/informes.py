# coding: utf-8
from django_rq import job
import django
import time
import utils
import re
import json

from easy_pdf.rendering import render_to_pdf
from django.template import loader
from escuelas.models import Perfil
from escuelas.serializers import EventoSerializer, PerfilSerializer


FORMATO_FECHA = "\d{4}-\d{2}-\d{2}"

def formatear_fecha(fecha_como_string):
    import datetime
    return datetime.datetime.strptime(fecha_como_string, "%Y-%m-%d").strftime("%d/%m/%Y")


@job
def generar_informe_de_perfil(perfil_id, desde, hasta):
    trabajo = utils.crear_modelo_trabajo("Informe de perfil {0} desde {1} hasta {2}".format(perfil_id, desde, hasta))

    if None in [perfil_id, desde, hasta]:
        trabajo.error = "No han especificado todos los argumentos: perfil_id, desde y hasta."
        trabajo.save()
        return

    if not re.match(FORMATO_FECHA, desde) or not re.match(FORMATO_FECHA, hasta):
        trabajo.error = "Las fechas están en formato incorrecto, deben ser YYYY-MM-DD."
        trabajo.save()
        return

    trabajo.actualizar_paso(1, 4, "Solicitando datos desde {0} hasta {1}".format(desde, hasta))


    perfil = Perfil.objects.get(id=perfil_id)
    perfil_serializado = {
        "nombre": perfil.nombre,
        "apellido": perfil.apellido,
        "dni": perfil.dni,
        "cargo": {
            "nombre": perfil.cargo.nombre
        },
        "region": {
            "numero": perfil.region.numero
        }
    }

    eventos = perfil.obtener_eventos_por_fecha(desde, hasta)
    eventos_serializados = EventoSerializer(eventos, many=True).data

    trabajo.actualizar_paso(1, 4, "Procesando {0} eventos".format(len(eventos_serializados)))

    trabajo.actualizar_paso(2, 4, "Generando archivo")
    trabajo.resultado = json.dumps({'perfil': perfil_serializado, 'cantidad_de_eventos': len(eventos_serializados)})

    template = loader.get_template('informe.html')
    contexto = {
        "perfil": perfil,
        "eventos": eventos,
        "desde": formatear_fecha(desde),
        "hasta": formatear_fecha(hasta),
    }

    contenido = render_to_pdf("informe.html", contexto)
    trabajo.archivo.save('informe_region_{0}_{1}_{2}_{3}.pdf'.format(perfil.region.numero, perfil.cargo.nombre, perfil.apellido, perfil.nombre), django.core.files.base.ContentFile(contenido))

    trabajo.actualizar_paso(4, 4, "Finalizando")
    trabajo.save()
    return trabajo
