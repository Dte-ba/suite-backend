# coding: utf-8
from __future__ import unicode_literals
import time
from django.core.management.base import BaseCommand
from escuelas import models
import progressbar
import requests

MODO_VERBOSE = True

def log(*k):
    global MODO_VERBOSE

    if MODO_VERBOSE:
        print(k)

BASE_URL = 'http://suite-api.dtelab.com.ar/api/'

def esperar(segundos):
    time.sleep(segundos)

def barra_de_progreso(simple=True):
    if simple:
        return progressbar.ProgressBar(widgets=[progressbar.SimpleProgress()])
    else:
        return progressbar.ProgressBar()

class Command(BaseCommand):
    help = 'Genera todos los datos iniciales.'

    def handle(self, *args, **options):

        self.crear_cargos_escolares()
        self.crear_regiones()
        self.crear_tipos_de_financiamiento()
        self.crear_niveles()
        self.crear_tipos_de_gestion()
        self.crear_areas()
        self.crear_programas()
        self.crear_cargos()
        self.crear_experiencias()
        self.crear_contratos()
        self.crear_motivos_de_tareas()
        self.crear_estados_de_tareas()
        self.crear_prioridades_de_tareas()
        self.crear_estados_de_validaciones()
        self.crear_motivos_de_conformaciones()
        self.crear_categorias_de_eventos()

        self.importar_distritos_y_localidades()
        self.importar_escuelas()
        self.importar_contactos()
        self.importar_pisos()
        self.vincular_programas()
        self.importar_tareas()
        self.importar_comentarios_de_tareas()
        self.importar_eventos()
        self.vincular_acompaniantes()
        self.importar_conformaciones()
        self.importar_validaciones()
        self.importar_comentarios_de_validaciones()

    def crear_regiones(self):
        numeros = range(1, 26)

        print("Creando Regiones")
        bar = barra_de_progreso()

        for n in bar(numeros):
            p, created = models.Region.objects.get_or_create(numero=n)
            log(p)

        p, created = models.Region.objects.get_or_create(numero=27)

        if MODO_VERBOSE:
            print(p)

    def importar_distritos_y_localidades(self):
        localidades = self.obtener_datos_desde_api('localidades')['localidades']

        print("Creando Localidades")
        bar = barra_de_progreso(simple=False)

        for localidad in bar(localidades):
            objeto_distrito, Localidadescreated = models.Distrito.objects.get_or_create(nombre=localidad['distrito'].title())
            objeto_localidad, created = models.Localidad.objects.get_or_create(nombre=localidad['localidad'].title())

            objeto_localidad.distrito = objeto_distrito
            objeto_localidad.save()

            objeto_distrito.region, created = models.Region.objects.get_or_create(numero=int(localidad['region']))
            objeto_distrito.save()

            if MODO_VERBOSE:
                print objeto_distrito, " -> ", objeto_localidad, "de la", objeto_distrito.region

    def importar_eventos(self):
        eventos = self.obtener_datos_desde_api('eventos')['eventos']

        print("Creando Eventos")
        bar = barra_de_progreso(simple=False)

        for evento in bar(eventos):
            legacy_id = evento['legacy_id']
            fecha_inicio = evento['fecha_inicio']
            hora_inicio = evento['hora_inicio']
            fecha_final = evento['fecha_final']
            hora_final = evento['hora_final']
            fecha_carga = evento['fecha_de_carga']
            cue = evento['cue']
            responsable = evento['usuario']
            dni_usuario = evento['dni_usuario']
            objetivo = evento['objetivo']
            cantidad_de_participantes = evento['cantidad_de_participantes']
            minuta = evento['minuta']
            acta = evento['acta']
            categoria = evento['categoria']
            subcategoria = evento['subcategoria']
            titulo = categoria + " " + subcategoria

            if MODO_VERBOSE:
                print "Se intenta buscar evento asociado a cue: " + str(cue)

            objeto_evento, created = models.Evento.objects.get_or_create(legacy_id=legacy_id)

            try:
                objeto_responsable = models.Perfil.objects.get(dni=dni_usuario)
            except models.Perfil.DoesNotExist:
                log("Error, no existe registro de usuario buscado %s. No se registrará el evento." %(dni_usuario))
                # cantidad_de_tareas_omitidas += 1
                continue

            try:
                objeto_escuela = models.Escuela.objects.get(cue=cue)
            except models.Escuela.DoesNotExist:
                log("Error, no existe la escuela buscada con cue %s. No se registrará el evento." %(cue))
                # cantidad_de_comentarios_de_tareas_omitidos += 1
                continue

            objeto_evento.titulo = titulo
            objeto_evento.fecha = fecha_inicio
            objeto_evento.inicio = hora_inicio
            objeto_evento.fecha_fin = fecha_final
            objeto_evento.fin = hora_final
            objeto_evento.responsable = objeto_responsable
            objeto_evento.escuela = objeto_escuela
            objeto_evento.save()


            if MODO_VERBOSE:
                print "=============================="
                print "   SE HA CREADO EL REGISTRO   "
                print "=============================="
                print "legacy_id:               " + str(legacy_id)
                print "Titulo:                  " + titulo
                print "Inicio:                  " + fecha_inicio + " " + hora_inicio
                print "Fin:                     " + fecha_final + " " + hora_final
                print "Categoria:               " + categoria
                print "Subcategoria:            " + subcategoria
                print "Objetivo:                " + objetivo
                print "Acta:                    " + acta
                print "Responsable:             " + objeto_responsable.apellido + ", " + objeto_responsable.nombre + " (dni " + dni_usuario + ")"
                print "Fecha de creacion:       " + fecha_carga
                print "Cant. de Participantes:  " + str(cantidad_de_participantes)
                print "Escuela:                 " + objeto_escuela.nombre + " " + str(cue)
                print "=============================="

    def importar_escuelas(self):
        resultado = self.obtener_datos_desde_api('escuelas')

        print("Se importarán %d escuelas en total." %(resultado['cantidad']))
        esperar(2)

        escuelas = resultado['escuelas']

        bar = barra_de_progreso(simple=False)

        for escuela in bar(escuelas):

            if MODO_VERBOSE:
                print "Intentando crear el registro escuela id_original:", escuela['id']

            objeto_escuela, created = models.Escuela.objects.get_or_create(cue=escuela['cue'])

            objeto_area, created = models.Area.objects.get_or_create(nombre=escuela['area'].title())

            objeto_localidad, created = models.Localidad.objects.get_or_create(nombre=escuela['localidad'].title())
            objeto_tipoDeFinanciamiento, created = models.TipoDeFinanciamiento.objects.get_or_create(nombre=escuela['tipo_financiamiento'].title())
            objeto_nivel, created = models.Nivel.objects.get_or_create(nombre=escuela['nivel'].title())
            objeto_tipoDeGestion, created = models.TipoDeGestion.objects.get_or_create(nombre=escuela['tipo_gestion'].title())
            #objeto_programa, created = models.Programa.objects.get_or_create(nombre=escuela['programa'].title())

            objeto_escuela.nombre = escuela['nombre'].title()
            objeto_escuela.direccion = escuela['direccion']
            objeto_escuela.telefono = escuela['telefono']
            objeto_escuela.latitud = escuela['latitud']
            objeto_escuela.longitud = escuela['longitud']

            objeto_escuela.area = objeto_area

            objeto_escuela.localidad = objeto_localidad
            objeto_escuela.tipoDeFinanciamiento = objeto_tipoDeFinanciamiento
            objeto_escuela.nivel = objeto_nivel
            objeto_escuela.tipoDeGestion = objeto_tipoDeGestion
            #objeto_escuela.programas = objeto_programa

            objeto_escuela.save()

            log("Se ha creado el registro:")
            log(objeto_escuela, "\n CUE: ", objeto_escuela.cue, "\n Direccion: ", objeto_escuela.direccion, "\n Tel: ", objeto_escuela.telefono, "\n ", objeto_escuela.localidad, "\n ", objeto_escuela.area, "\n ", objeto_escuela.nivel, "\n ", objeto_escuela.tipoDeFinanciamiento, "\n ", objeto_escuela.tipoDeGestion)
            log("===========")

    def importar_conformaciones(self):
        resultado = self.obtener_datos_desde_api('conformaciones')

        print("Se importarán %d conformaciones en total." %(resultado['cantidad']))
        esperar(2)

        conformaciones = resultado['conformaciones']

        bar = barra_de_progreso(simple=False)

        for conformacion in bar(conformaciones):

            cue_conformado = conformacion['cue_conformado']
            cue_principal = conformacion['cue_principal']
            motivo = conformacion['motivo']
            fecha = conformacion['fecha']

            if MODO_VERBOSE:
                print "Intentando crear conformacion de escuela `", cue_conformado, "` con la escuela padre ", cue_principal, " y motivo ", motivo
                print "======================================================================================================"
                print "Escuela ", cue_conformado, " queda conformada con padre ", cue_principal
                print "Fecha:   ", fecha
                print "Motivo:  ", motivo
                print "======================================================================================================"

            objeto_escuela = models.Escuela.objects.get(cue=cue_conformado)
            escuela_padre = models.Escuela.objects.get(cue=cue_principal)
            objeto_motivo = models.MotivoDeConformacion.objects.get(nombre=motivo)

            objeto_escuela.padre = escuela_padre
            objeto_escuela.fechaConformacion = fecha
            objeto_escuela.motivoDeConformacion = objeto_motivo

            objeto_escuela.save()

    def importar_validaciones(self):
        resultado = self.obtener_datos_desde_api('validaciones')
        cantidad_de_validaciones_creadas = 0
        cantidad_de_validaciones_omitidas = 0
        cantidad_de_validaciones_sin_escuela = 0
        cantidad_de_validaciones_sin_usuario = 0
        cantidad_de_validaciones_con_motivo_erroneo = 0

        print("Se importarán %d validaciones en total." %(resultado['cantidad']))
        esperar(2)

        validaciones = resultado['validaciones']

        bar = barra_de_progreso(simple=False)

        for validacion in bar(validaciones):

            legacy_id = validacion['legacy_id']
            cue = validacion['cue']
            escuela = validacion['escuela']
            dni_usuario = validacion['dni_usuario']
            usuario = validacion['usuario']
            estado = validacion['estado']
            fecha = validacion['fecha_de_alta']

            if estado==1:
                estado = "Pendiente"
            elif estado==2:
                estado = "Objetada"
            elif estado==3:
                estado = "Aprobada"
            else:
                estado = "NO IMPORTAR"

            if MODO_VERBOSE:
                print "Intentando crear validacion con legacy_id ", legacy_id, " y estado ", estado
                print "======================================================================================================"
                print "Escuela ", escuela, "  ", cue
                print "Usuario: ", usuario, " (", dni_usuario, ")"
                print "Fecha:   ", fecha
                print "Estado:  ", estado
                print "======================================================================================================"


            try:
                objeto_escuela = models.Escuela.objects.get(cue=cue)
            except models.Escuela.DoesNotExist:
                log("Error, no existe la escuela con cue %s. Se ignora el registro." %(cue))
                cantidad_de_validaciones_omitidas += 1
                cantidad_de_validaciones_sin_escuela += 1
                continue

            try:
                objeto_usuario = models.Perfil.objects.get(dni=dni_usuario)
            except models.Perfil.DoesNotExist:
                log("Error, no existe el usuario con dni %s. Se ignora el registro." %(dni_usuario))
                cantidad_de_validaciones_omitidas += 1
                cantidad_de_validaciones_sin_usuario += 1
                continue



            try:
                objeto_estado = models.EstadoDeValidacion.objects.get(nombre=estado)
            except models.EstadoDeValidacion.DoesNotExist:
                log("Error, estado %s no corresponde. Se ignora el registro." %(estado))
                cantidad_de_validaciones_omitidas += 1
                cantidad_de_validaciones_con_motivo_erroneo += 1
                continue


            objeto_validacion, created = models.Validacion.objects.get_or_create(legacy_id=legacy_id)
            objeto_validacion.fechaDeAlta = fecha
            objeto_validacion.autor = objeto_usuario
            objeto_validacion.estado = objeto_estado
            objeto_validacion.escuela = objeto_escuela

            objeto_validacion.save()

            cantidad_de_validaciones_creadas += 1

        print("Resumen de validaciones:")
        print("   Se crearon %d validaciones correctamente." %(cantidad_de_validaciones_creadas))
        print("   Se evitaron crear %d validaciones:" %(cantidad_de_validaciones_omitidas))
        print("     No se encontró la escuela de %s validaciones:" %(cantidad_de_validaciones_sin_escuela))
        print("     No se encontró el usuario de %s validaciones:" %(cantidad_de_validaciones_sin_usuario))
        print("     Hay %s validaciones con estado erróneo:" %(cantidad_de_validaciones_con_motivo_erroneo))

    def importar_comentarios_de_validaciones(self):
        resultado = self.obtener_datos_desde_api('historial_validaciones')
        cantidad_de_validaciones_creadas = 0
        cantidad_de_validaciones_omitidas = 0
        cantidad_de_validaciones_sin_escuela = 0
        cantidad_de_validaciones_sin_usuario = 0
        cantidad_de_validaciones_con_motivo_erroneo = 0

        print("Se importarán %d comentarios de validaciones en total." %(resultado['cantidad']))
        esperar(2)

        comentarios = resultado['historial_validaciones']

        bar = barra_de_progreso(simple=False)

        for comentario in bar(comentarios):

            cantidad = comentario['cantidad']
            usuario = comentario['usuario']
            dni_usuario = comentario['dni_usuario']
            fecha = comentario['fecha']
            legacy_id = comentario['legacy_id']
            validacion = comentario['validacion_legacy_id']
            comentario = comentario['observaciones']

            if MODO_VERBOSE:
                print "Intentando crear comentario de validacion con legacy_id ", legacy_id
                print "======================================================================================================"
                print "ID Validacion:", validacion
                print "Usuario: ", usuario, " (", dni_usuario, ")"
                print "Fecha:   ", fecha
                print "Comentario:  ", comentario
                print "======================================================================================================"


            try:
                objeto_usuario = models.Perfil.objects.get(dni=dni_usuario)
            except models.Perfil.DoesNotExist:
                log("Error, no existe el usuario con dni %s. Se ignora el registro." %(dni_usuario))
                cantidad_de_validaciones_omitidas += 1
                cantidad_de_validaciones_sin_usuario += 1
                continue

            try:
                objeto_validacion = models.Validacion.objects.get(legacy_id=validacion)
            except models.Validacion.DoesNotExist:
                log("Error, no existe la validacion con legacy_id %s. Se ignora el registro." %(validacion))
                cantidad_de_validaciones_omitidas += 1
                cantidad_de_validaciones_con_motivo_erroneo += 1
                continue


            objeto_comentario_de_validacion, created = models.ComentarioDeValidacion.objects.get_or_create(legacy_id=legacy_id)
            objeto_comentario_de_validacion.validacion = objeto_validacion
            objeto_comentario_de_validacion.fecha = fecha
            objeto_comentario_de_validacion.autor = objeto_usuario
            objeto_comentario_de_validacion.comentario = comentario
            objeto_comentario_de_validacion.cantidad = cantidad

            objeto_comentario_de_validacion.save()

            cantidad_de_validaciones_creadas += 1

        print("Resumen de comentarios de validaciones:")
        print("   Se crearon %d comentarios correctamente." %(cantidad_de_validaciones_creadas))
        print("   Se evitaron crear %d comentarios:" %(cantidad_de_validaciones_omitidas))
        print("     No se encontró la validacion correspondiente a %s comentarios:" %(cantidad_de_validaciones_con_motivo_erroneo))
        print("     No se encontró el usuario de %s comentarios:" %(cantidad_de_validaciones_sin_usuario))


    def importar_contactos(self):
        contactos = self.obtener_datos_desde_api('contactos')['contactos']

        print("Importando Contactos")
        bar = barra_de_progreso(simple=False)

        for contacto in bar(contactos):
            log("Buscando escuela para el contacto: ", contacto['escuela'])
            objeto_escuela = models.Escuela.objects.get(cue=contacto['escuela'])
            objeto_cargo = models.CargoEscolar.objects.get(nombre=contacto['cargo'])
            objeto_contacto, created = models.Contacto.objects.get_or_create(nombre=contacto['nombre'].title())
            #
            objeto_contacto.cargo = objeto_cargo
            objeto_contacto.escuela = objeto_escuela
            if contacto['email']:
                objeto_contacto.email = contacto['email'].lower()

            objeto_contacto.telefono_particular = contacto['telefono']
            objeto_contacto.telefono_celular = contacto['celular']
            if contacto['horario']:
                objeto_contacto.horario = contacto['horario'].title()

            objeto_contacto.save()

            log("Se ha creado el registro:")
            log("Nombre: ", objeto_contacto, "\n Teléfono Particular ", objeto_contacto.telefono_particular, "\n Teléfono Celular: ", objeto_contacto.telefono_celular, "\n Email: ", objeto_contacto.email, "\n Horario: ", objeto_contacto.horario)
            log("===========")

    def importar_pisos(self):
        pisos = self.obtener_datos_desde_api('pisos')['pisos']

        print("Importando Pisos")
        bar = barra_de_progreso(simple=False)

        for piso in bar(pisos):

            if piso['marca']:
                marca = piso['marca']
            else:
                marca = "Desconocido"

            log("Buscando piso para escuela: ", piso['cue'])
            objeto_escuela = models.Escuela.objects.get(cue=piso['cue'])
            objeto_piso, created = models.Piso.objects.get_or_create(servidor=marca)
            #
            objeto_piso.serie = piso['serie']

            if piso['ups']:
                if piso['ups'] == "SI":
                    objeto_piso.ups = True
                else:
                    objeto_piso.ups = False
            else:
                objeto_piso.ups = False


            if piso['rack']:
                if piso['rack'] == "SI":
                    objeto_piso.rack = True
                else:
                    objeto_piso.rack = False
            else:
                objeto_piso.rack = False

            objeto_piso.estado = piso['piso_estado']

            objeto_escuela.piso = objeto_piso

            objeto_piso.save()
            objeto_escuela.save()

            log("Se ha creado el registro:")
            log("Piso de escuela ", piso['cue'], ": \n Servidor: ", piso['marca'], "\n Serie: ", piso['serie'], "\n UPS: ", piso['ups'], "\n Rack: ", piso['rack'], "\n Estado: ", piso['piso_estado'])
            log("===========")

    def importar_tareas(self):
        tareas = self.obtener_datos_desde_api('tickets')['tickets']
        cantidad_de_tareas_creadas = 0
        cantidad_de_tareas_omitidas = 0

        print("Importando Tareas")
        bar = barra_de_progreso(simple=False)

        for tarea in bar(tareas):
            log("Se intenta crear el registro con id_original: " + str(tarea['id_ticket_original']) + " y DNI de usuario: " + str(tarea['dni_usuario']))
            log("Prioridad de la tarea: " + str(tarea['prioridad']))
            log("Motivo de la tarea: " + unicode(tarea['motivo']))
            log("Estado de la tarea: " + str(tarea['estado']))

            dni_usuario = tarea['dni_usuario']

            try:
                objeto_autor = models.Perfil.objects.get(dni=dni_usuario)
            except models.Perfil.DoesNotExist:
                log("Error, no existe registro de usuario buscado %s. No se registrará la tarea." %(dni_usuario))
                cantidad_de_tareas_omitidas += 1
                continue

            objeto_tarea, created = models.Tarea.objects.get_or_create(id_ticket_original=tarea['id_ticket_original'])

            objeto_escuela = models.Escuela.objects.get(cue=tarea['cue'])
            objeto_motivo = models.MotivoDeTarea.objects.get(nombre=tarea['motivo'])
            objeto_estado = models.EstadoDeTarea.objects.get(nombre=tarea['estado'])

            prioridad = tarea['prioridad']
            if prioridad == 1:
                prioridad = "Alta"
            elif prioridad == 2:
                prioridad = "Media"
            elif prioridad == 3:
                prioridad = "Baja"

            objeto_prioridad = models.PrioridadDeTarea.objects.get(nombre=prioridad)

            fecha_alta = tarea['fecha_alta']
            #
            objeto_tarea.fechaDeAlta = fecha_alta
            objeto_tarea.titulo = "Tarea #: " + str(tarea['id_ticket_original'])
            objeto_tarea.descripcion = tarea['descripcion']
            objeto_tarea.autor = objeto_autor
            objeto_tarea.escuela = objeto_escuela
            objeto_tarea.motivoDeTarea = objeto_motivo
            objeto_tarea.estadoDeTarea = objeto_estado
            objeto_tarea.prioridadDeTarea = objeto_prioridad

            objeto_tarea.save()


            log("Se ha creado el registro:")
            log("Tarea con id_original: " + str(tarea['id_ticket_original']))
            log("===========")
            cantidad_de_tareas_creadas += 1

        print("Resumen de tareas:")
        print("   Se crearon %d tareas correctamente." %(cantidad_de_tareas_creadas))
        print("   Se evitaron crear %d tareas porque correspondían a usuarios inexistentes." %(cantidad_de_tareas_omitidas))

    def importar_comentarios_de_tareas(self):
        comentarios = self.obtener_datos_desde_api('comentarios_tickets')['comentarios_tickets']
        cantidad_de_comentarios_de_tareas_creados = 0
        cantidad_de_comentarios_de_tareas_omitidos = 0

        print("Importando Comentarios de Tareas")
        bar = barra_de_progreso(simple=False)

        for comentario in bar(comentarios):
            log("Se intenta crear el registro con id_original: " + str(comentario['id_ticket_original']) + " y DNI de usuario: " + str(comentario['dni_usuario']))

            dni_usuario = comentario['dni_usuario']
            id_ticket_original = comentario['id_ticket_original']

            try:
                objeto_autor = models.Perfil.objects.get(dni=dni_usuario)
            except models.Perfil.DoesNotExist:
                log("Error, no existe registro de usuario buscado %s. No se registrará la tarea." %(dni_usuario))
                cantidad_de_comentarios_de_tareas_omitidos += 1
                continue

            try:
                objeto_tarea = models.Tarea.objects.get(id_ticket_original=id_ticket_original)
            except models.Tarea.DoesNotExist:
                log("Error, no existe registro de tarea buscado %s. No se registrará el comentario." %(id_ticket_original))
                cantidad_de_comentarios_de_tareas_omitidos += 1
                continue



            objeto_comentario, created = models.ComentarioDeTarea.objects.get_or_create(comentario=comentario['comentario'])
            objeto_comentario.autor = objeto_autor
            objeto_comentario.fechaDeAlta = comentario['fecha']
            objeto_comentario.tarea = objeto_tarea

            objeto_comentario.save()


            log("Se ha creado el registro:")
            log("Comentario de Tarea con id_original: " + str(comentario['id_ticket_original']))
            log("===========")
            cantidad_de_comentarios_de_tareas_creados += 1

        print("Resumen de tareas:")
        print("   Se crearon %d comentarios de tareas correctamente." %(cantidad_de_comentarios_de_tareas_creados))
        print("   Se evitaron crear %d comentarios de tareas porque correspondían a usuarios inexistentes." %(cantidad_de_comentarios_de_tareas_omitidos))

    def vincular_programas(self):
        programas = self.obtener_datos_desde_api('programas')['programas']

        print("Vinculando Programas")
        bar = barra_de_progreso(simple=False)

        for programa in bar(programas):
            log("Busando programas para escuela: ", programa['cue'])

            objeto_escuela = models.Escuela.objects.get(cue=programa['cue'])

            objeto_escuela.programas.add(models.Programa.objects.get(nombre=programa['programa']))

            objeto_escuela.save()

            log("Se ha vinculado el registro:")
            log("Programa: ", programa['programa'], "a la escuela con CUE ", programa['cue'])
            log("===========")

    def vincular_acompaniantes(self):
        acompaniantes = self.obtener_datos_desde_api('acompaniantes_eventos')['acompaniantes_eventos']

        print("Vinculando Acompañantes de eventos")
        bar = barra_de_progreso(simple=False)

        for acompaniante in bar(acompaniantes):

            legacy_id = acompaniante['legacy_id']
            dni_usuario = acompaniante['dni_usuario']

            log("Busando acompaniantes para legacy_id: ", legacy_id)

            try:
                objeto_evento = models.Evento.objects.get(legacy_id=legacy_id)
            except models.Evento.DoesNotExist:
                log("Error, no existe registro de evento con legacy_id %s. No se registrará el acompañante." %(legacy_id))
                # cantidad_de_comentarios_de_tareas_omitidos += 1
                continue

            try:
                objeto_acompaniante = models.Perfil.objects.get(dni=dni_usuario)
            except models.Perfil.DoesNotExist:
                log("Error, no existe registro de usuario buscado %s. No se registrará el acompañante." %(dni_usuario))
                # cantidad_de_tareas_omitidas += 1
                continue

            objeto_evento.acompaniantes.add(models.Perfil.objects.get(dni=dni_usuario))

            objeto_evento.save()

            log("Se ha vinculado el registro:")
            log("Acomaniante: ", acompaniante['nombre'], "al evento con legacy_id ", acompaniante['legacy_id'])
            log("===========")

    def obtener_datos_desde_api(self, data):
        url = BASE_URL + data
        print("Consultando la URL: " + url)
        resultado = requests.get(url)
        return resultado.json()

    def crear_tipos_de_financiamiento(self):
        nombres = ["Nacional", "Provincial", "Municipal", "Propio"]

        print("Creando Tipos de Financiamiento")
        bar = barra_de_progreso()

        for nombre in bar(nombres):
            p, created = models.TipoDeFinanciamiento.objects.get_or_create(nombre=nombre)
            log(p)

    def crear_motivos_de_tareas(self):
        nombres = [
            "Servidor robado",
            "Servidor roto",
            "Piso tecnológico",
            "Paquetes de provisión",
            "Movimiento de equipamiento",
            "Problemas eléctricos",
            "Switch roto",
            "UPS roto",
            "Mantenimiento básico de piso",
            "Ampliacion de piso",
            "Reingeniería de piso",
            "Mudanza de piso",
            "Reclamos del territorio"
        ]

        print("Creando Motivos de Tareas")
        bar = barra_de_progreso()

        for nombre in bar(nombres):
            p, created = models.MotivoDeTarea.objects.get_or_create(nombre=nombre)
            log(p)

    def crear_motivos_de_conformaciones(self):
        nombres = [
            "Comparte Piso",
            "Comparte Edificio",
            "CUE Nuevo",
            "CUE Anterior",
            "Se Unificó"
        ]

        print("Creando Motivos de Conformaciones")
        bar = barra_de_progreso()

        for nombre in bar(nombres):
            p, created = models.MotivoDeConformacion.objects.get_or_create(nombre=nombre)
            log(p)

    def crear_estados_de_tareas(self):
        nombres = [
            "Abierto",
            "En Progreso",
            "En Espera",
            "Cerrado"
        ]

        print("Creando Estados de Tareas")
        bar = barra_de_progreso()

        for nombre in bar(nombres):
            p, created = models.EstadoDeTarea.objects.get_or_create(nombre=nombre)
            log(p)

    def crear_estados_de_validaciones(self):
        nombres = [
            "Pendiente",
            "Objetada",
            "Aprobada"
            # "Pendiente", #1
            # "Revisión", #2
            # "Cerrado", #3,
            # "Eliminado", #4
            # "Conformacion", #5
            # "No valida" #6
        ]

        print("Creando Estados de Validaciones")
        bar = barra_de_progreso()

        for nombre in bar(nombres):
            p, created = models.EstadoDeValidacion.objects.get_or_create(nombre=nombre)
            log(p)

    def crear_prioridades_de_tareas(self):
        nombres = [
            "Alta",
            "Media",
            "Baja"
        ]

        print("Creando Prioridades de Tareas")
        bar = barra_de_progreso()

        for nombre in bar(nombres):
            p, created = models.PrioridadDeTarea.objects.get_or_create(nombre=nombre)
            log(p)

    def crear_niveles(self):
        nombres = ["Inicial", "Primaria", "Secundaria", "Superior"]

        print("Creando Niveles")
        bar = barra_de_progreso()

        for nombre in bar(nombres):
            p, created = models.Nivel.objects.get_or_create(nombre=nombre)
            log(p)

    def crear_tipos_de_gestion(self):
        nombres = ["Estatal", "Privada", "Compartida"]

        print("Creando Tipos de Gestión")
        bar = barra_de_progreso()

        for nombre in bar(nombres):
            p, created = models.TipoDeGestion.objects.get_or_create(nombre=nombre)
            log(p)

    def crear_areas(self):
        nombres = ["Urbana", "Rural"]

        print("Creando Areas")
        bar = barra_de_progreso()

        for nombre in bar(nombres):
            p, created = models.Area.objects.get_or_create(nombre=nombre)
            log(p)

    def crear_programas(self):
        nombres = [
            "Conectar Igualdad",
            "PAD",
            "Responsabilidad Empresarial",
            "Primaria Digital",
            "Escuelas del Futuro"
            ]

        print("Creando Programas")
        bar = barra_de_progreso()

        for nombre in bar(nombres):
            p, created = models.Programa.objects.get_or_create(nombre=nombre)
            log(p)

    def crear_experiencias(self):
        nombres = [
            "Técnico",
            "Pedagógico",
            "Administrativo",
            "Diseño",
            "Comunicación"
            ]

        print("Creando Experiencias")
        bar = barra_de_progreso()

        for nombre in bar(nombres):
            p, created = models.Experiencia.objects.get_or_create(nombre=nombre)
            log(p)

    def crear_contratos(self):
        nombres = [
            "PLANIED",
            "Planta/PLANIED",
            "Planta",
            "ConIg",
            "Ord. Tec."

            ]

        print("Creando Contactos")
        bar = barra_de_progreso()


        for nombre in bar(nombres):
            p, created = models.Contrato.objects.get_or_create(nombre=nombre)
            log(p)

    def crear_cargos(self):
        nombres = [
            ("FED", "Facilitador Educación Digital"),
            ("Coord", "Coordinador"),
            ("Adm", "Administrativo"),
            ("Coord EF", "Coordinador EF"),
            ("FED esp", "Facilitador Educación Digital Especial"),
            ("Coord Prov", "Coordinador Provincial")
            ]

        print("Creando Cargos")
        bar = barra_de_progreso()

        for nombre in bar(nombres):
            p, created = models.Cargo.objects.get_or_create(nombre=nombre[0], descripcion=nombre[1])
            log(p)

    def crear_cargos_escolares(self):
        nombres = [
            "Director",
            "Vice Director",
            "Secretario",
            "Maestro",
            "EMATP",
            "Prosecretario",
            "Preceptor",
            "Profesor",
            "Otro"
            ]

        print("Creando Cargos Escolares")
        bar = barra_de_progreso()

        for nombre in bar(nombres):
            p, created = models.CargoEscolar.objects.get_or_create(nombre=nombre)
            log(p)

    def crear_categorias_de_eventos(self):
        nombres = [
            "Acciones especiales/Congresos",
            "Acciones especiales/Desembarcos",
            "Acciones especiales/Encuentros masivos",
            "Acciones especiales/Prácticas profesionales",
            "Asistencia/Administrativa",
            "Asistencia/Pedagógica",
            "Asistencia/Técnica",
            "Escuelas del futuro/Seguimiento de actividades",
            "Escuelas del futuro/Seguimiento de acciones",
            "Capacitaciones/Sensibilización",
            "Capacitaciones/Docentes",
            "Capacitaciones/Alumnos",
            "Reunión/Online",
            "Reunión/Inspectores",
            "Reunión/Referente de área",
            "Reunión/Equipo",
            "Reunión/Planificación",
            "Reunión/Región Central",
            ]

        print("Creando Categorías de eventos")
        bar = barra_de_progreso()

        for nombre in bar(nombres):
            p, created = models.CategoriaDeEvento.objects.get_or_create(nombre=nombre)
            log(p)
