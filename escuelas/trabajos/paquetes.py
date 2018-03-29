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


@job
def exportar_paquetes(inicio, fin, estadoPedido):
    trabajo = utils.crear_modelo_trabajo("Exportación de paquetes de estado {0} completo desde {1} hasta {2}".format(estadoPedido, inicio, fin))

    try:
        directorio_temporal = tempfile.mkdtemp()
        directorio_del_archivo_zip = tempfile.mkdtemp()

        trabajo.actualizar_paso(1, 3, 'Solicitando paquetes de estado "{0}" desde {1} hasta {2}'.format(estadoPedido, inicio, fin))

        data = models.Paquete.obtener_paquetes_para_exportar(inicio, fin, estadoPedido)

        trabajo.actualizar_paso(1, 3, "Se van a exportar {0} paquetes".format(len(data['tabla'])))
        trabajo.actualizar_paso(1, 3, "Para solicitar estos paquetes se van a exportar {0} llaves".format(len(data['llaves'])))

        trabajo.actualizar_paso(1, 3, "Creando estructura para el archivo .zip")

        llaves = data['llaves']
        data['llaves'] = [str(llave) for llave in data['llaves']]

        # copia las llaves al directorio temporal que se comprimirá
        for llave in llaves:
            trabajo.actualizar_paso(1, 3, "Copiando llave {0}".format(llave.name))
            shutil.copy(llave.path, directorio_temporal)

        crear_listado_excel_de_paquetes(data['tabla'], directorio_temporal)

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

        trabajo.actualizar_paso(2, 3, "Generando archivo comprimido")

        # Si se pidió exportar los paquetes Pendientes, y el estado del paquete era Pendiente, cambiarlo por EducAr
        # Esto es para evitar que al exportar Todos, se actualicen los paquetes.
        # Se guarda la fecha en que se hizo el pedido
        if estadoPedido == "Pendiente":
            trabajo.actualizar_paso(2, 3, "Cambiando paquetes desde el estado Pendiente a EducAr")
            models.Paquete.marcar_paquetes_pendientes_como_enviados_a_educar(inicio, fin)
        else:
            trabajo.actualizar_paso(2, 3, "No se cambiara el estado de ningun paquete")

        trabajo.actualizar_paso(3, 3, "Finalizado")

        # Elimina los directorios temporales (y el .zip temporal)
        shutil.rmtree(directorio_temporal)
        shutil.rmtree(directorio_del_archivo_zip)
    except Exception as e:
        trabajo.error = str(e)
        trabajo.save()
        raise Exception(e)

    return trabajo

def crear_listado_excel_de_paquetes(datos, directorio_destino):
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Paquetees')

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['CUE', 'Escuela', 'Región', 'Distrito', 'Nro Serie Servidor', 'ID Hardware', 'Marca de Arranque', 'NE', 'Pedido', 'Estado']
    col_num = 2 # 0 y 1 son obligatorias

    # Escribir los headers
    for col_num in range(len(columns)):
        ws.write(0, col_num, columns[col_num], font_style)

    ws.col(0).width = 256 * 12
    ws.col(1).width = 256 * 12
    ws.col(2).width = 256 * 18
    ws.col(3).width = 256 * 30

    font_style = xlwt.XFStyle()

    row_num = 0

    for fila in datos:
        row_num += 1
        ws.write(row_num, 0, fila["cue"], font_style)
        ws.write(row_num, 1, fila["escuela"], font_style)
        ws.write(row_num, 2, fila["region"], font_style)
        ws.write(row_num, 3, fila["distrito"], font_style)
        ws.write(row_num, 4, fila["serie_servidor"], font_style)
        ws.write(row_num, 5, fila["id_hardware"], font_style)
        ws.write(row_num, 6, fila["marca_de_arranque"], font_style)
        ws.write(row_num, 7, fila["ne"], font_style)
        ws.write(row_num, 8, fila["pedido"], font_style)
        ws.write(row_num, 9, fila["estado"], font_style)
        ws.write(row_num, 10, fila["llave_servidor"], font_style)

    ruta_para_el_archivo = os.path.join(directorio_destino, "listado_de_paquetes.xls")

    wb.save(ruta_para_el_archivo)
