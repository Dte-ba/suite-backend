# coding: utf-8
from __future__ import unicode_literals

import time
from django.core.management.base import BaseCommand
from escuelas import models
import progressbar
import requests

MODO_VERBOSE = False

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
        self.importar_distritos_y_localidades()
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

        self.importar_escuelas()
        self.importar_contactos()
        self.importar_pisos()
        self.vincular_programas()
        self.importar_tareas()
        self.importar_comentarios_de_tareas()

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
            objeto_distrito, created = models.Distrito.objects.get_or_create(nombre=localidad['distrito'].title())
            objeto_localidad, created = models.Localidad.objects.get_or_create(nombre=localidad['localidad'].title())

            objeto_localidad.distrito = objeto_distrito
            objeto_localidad.save()

            objeto_distrito.region, created = models.Region.objects.get_or_create(numero=int(localidad['region']))
            objeto_distrito.save()

            if MODO_VERBOSE:
                print objeto_distrito, " -> ", objeto_localidad, "de la", objeto_distrito.region

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

            dni_usuario = tarea['dni_usuario']

            try:
                objeto_autor = models.Perfil.objects.get(dni=dni_usuario)
            except models.Perfil.DoesNotExist:
                log("Error, no existe registro de usuario buscado %s. No se registrará la tarea." %(dni_usuario))
                cantidad_de_tareas_omitidas += 1
                continue

            objeto_tarea, created = models.Tarea.objects.get_or_create(id_ticket_original=tarea['id_ticket_original'])

            objeto_escuela = models.Escuela.objects.get(cue=tarea['cue'])
            objeto_motivo = models.MotivoTarea.objects.get(nombre=tarea['motivo'])
            objeto_estado = models.EstadoTarea.objects.get(nombre=tarea['estado'])

            prioridad = tarea['prioridad']
            if prioridad == 1:
                prioridad = "Alta"
            elif prioridad == 2:
                prioridad = "Media"
            elif prioridad == 3:
                prioridad = "Baja"

            objeto_prioridad = models.PrioridadTarea.objects.get(nombre=prioridad)

            fecha_alta = tarea['fecha_alta']
            #
            objeto_tarea.fechaDeAlta = fecha_alta
            objeto_tarea.titulo = "Tarea #: " + str(tarea['id_ticket_original'])
            objeto_tarea.descripcion = tarea['descripcion']
            objeto_tarea.autor = objeto_autor
            objeto_tarea.escuela = objeto_escuela
            objeto_tarea.motivo = objeto_motivo
            objeto_tarea.estado = objeto_estado
            objeto_tarea.prioridad = objeto_prioridad

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



            objeto_comentario, created = models.ComentarioTarea.objects.get_or_create(comentario=comentario['comentario'])
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
            p, created = models.MotivoTarea.objects.get_or_create(nombre=nombre)
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
            p, created = models.EstadoTarea.objects.get_or_create(nombre=nombre)
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
            p, created = models.PrioridadTarea.objects.get_or_create(nombre=nombre)
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
