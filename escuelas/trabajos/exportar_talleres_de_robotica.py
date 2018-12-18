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

from escuelas import models

@job("default", timeout=5*60)
def exportar_talleres(inicio, fin, criterio):

    trabajo = utils.crear_modelo_trabajo("Exportación de talleres segun criterio {0} completo desde {1} hasta {2}".format(criterio, inicio, fin))

    directorio_temporal = tempfile.mkdtemp()

    if criterio:
        if criterio == "fechaDeRealizacion":
            eventos = models.EventoDeRobotica.objects.filter(fecha__range=(inicio, fin))
        else:
            eventos = models.EventoDeRobotica.objects.filter(fecha_de_creacion__range=(inicio, fin))

    # if region:
    #     eventos = eventos.filter(escuela__localidad__distrito__region__numero=region)

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Talleres')

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Fecha de Creación', 'Fecha', 'Hora Inicio', 'Hora Fin', 'Título', 'Área', 'Curso', 'Sección', 'Cant. de Alumnos', 'Tallerista', 'Escuela', 'CUE', 'Región', 'Distrito', 'Localidad', 'Docente a Cargo', 'Se realizó el taller?', 'Motivo si NO se realizó', 'Acta', 'Estado', 'Observaciones']
    col_num = 2 # 0 y 1 son obligatorias

    # Escribir los headers
    for col_num in range(len(columns)):
        ws.write(0, col_num, columns[col_num], font_style)


    ws.col(0).width = 512 * 12 # Fecha de Creación
    ws.col(1).width = 256 * 12 # Fecha
    ws.col(2).width = 256 * 12 # Hora Inicio
    ws.col(3).width = 256 * 12 # Hora Fin
    ws.col(4).width = 600 * 12 # Titulo
    ws.col(5).width = 400 * 12 # Área
    ws.col(6).width = 256 * 12 # Curso
    ws.col(7).width = 256 * 12 # Sección
    ws.col(8).width = 256 * 12 # Cantidad de Alumnos
    ws.col(9).width = 600 * 12 # Tallerista
    ws.col(10).width = 600 * 12 # Escuela
    ws.col(11).width = 256 * 12 # CUE
    ws.col(12).width = 200 * 12 # Región
    ws.col(13).width = 400 * 12 # Distrito
    ws.col(14).width = 400 * 12 # Localidad
    ws.col(15).width = 600 * 12 # Docente a Cargo
    ws.col(16).width = 600 * 12 # Se pudo realizar el taller?
    ws.col(17).width = 600 * 12 # Si no se pudo, motivo.
    ws.col(18).width = 256 * 12 # Acta
    ws.col(19).width = 300 * 12 # Estado
    ws.col(20).width = 600 * 12 # Observaciones

    font_style = xlwt.XFStyle()

    row_num = 0
    total = eventos.count()

    trabajo.actualizar_paso(row_num, total, "Comenzando a exportar {} registros".format(total))

    for taller in eventos:
        if row_num % 400 == 0:
            trabajo.actualizar_paso(row_num, total, "Procesando {} de {} registros".format(row_num, total))

        fecha_de_creacion = taller.fecha_de_creacion
        fecha_de_creacion = fecha_de_creacion.strftime("%d-%m-%Y")
        fecha = taller.fecha
        fecha = fecha.strftime("%d-%m-%Y")
        hora_inicio = taller.inicio
        hora_inicio = hora_inicio.strftime("%H:%m")
        hora_fin = taller.fin
        hora_fin = hora_fin.strftime("%H:%m")
        titulo = taller.titulo.nombre
        region = taller.escuela.localidad.distrito.region.numero
        distrito = taller.escuela.localidad.distrito.nombre
        localidad = taller.escuela.localidad.nombre
        cue = taller.escuela.cue
        escuela = taller.escuela.nombre
        tallerista = taller.tallerista.apellido + ", " + taller.tallerista.nombre
        area = taller.area_en_que_se_dicta.nombre
        curso = taller.curso.nombre
        seccion = taller.seccion.nombre
        cantidad_de_alumnos = taller.cantidad_de_alumnos
        docente_a_cargo = taller.docente_a_cargo
        se_dio_el_taller = taller.se_dio_el_taller
        motivo = taller.motivo
        observaciones = taller.minuta
        acta = taller.acta

        if acta:
            acta = "Con Acta"
        else:
            acta = "Sin Acta"

        cerrar_evento = taller.cerrar_evento
        if cerrar_evento == True:
            estado = "Cerrado"
        else:
            estado = "Abierto"

        row_num += 1

        ws.write(row_num, 0, fecha_de_creacion, font_style)
        ws.write(row_num, 1, fecha, font_style)
        ws.write(row_num, 2, hora_inicio, font_style)
        ws.write(row_num, 3, hora_fin, font_style)
        ws.write(row_num, 4, titulo, font_style)
        ws.write(row_num, 5, area, font_style)
        ws.write(row_num, 6, curso, font_style)
        ws.write(row_num, 7, seccion, font_style)
        ws.write(row_num, 8, cantidad_de_alumnos, font_style)
        ws.write(row_num, 9, tallerista, font_style)
        ws.write(row_num, 10, escuela, font_style)
        ws.write(row_num, 11, cue, font_style)
        ws.write(row_num, 12, region, font_style)
        ws.write(row_num, 13, distrito, font_style)
        ws.write(row_num, 14, localidad, font_style)
        ws.write(row_num, 15, docente_a_cargo, font_style)
        ws.write(row_num, 16, se_dio_el_taller, font_style)
        ws.write(row_num, 17, motivo, font_style)
        ws.write(row_num, 18, acta, font_style)
        ws.write(row_num, 19, estado, font_style)
        ws.write(row_num, 20, observaciones, font_style)

    ruta_para_el_archivo = os.path.join(directorio_temporal, "listado_de_talleres.xls")

    wb.save(ruta_para_el_archivo)

    archivo = open(ruta_para_el_archivo)
    trabajo.archivo.save(u"exportacion_de_talleres_{0}_hasta_{1}_segun_{2}.xls".format(inicio, fin, criterio), django.core.files.base.File(archivo))
    archivo.close()

    trabajo.resultado = json.dumps({'data': "ok"})
    trabajo.save()

    shutil.rmtree(directorio_temporal)

    trabajo.actualizar_paso(total, total, "Finalizado")

    return trabajo
