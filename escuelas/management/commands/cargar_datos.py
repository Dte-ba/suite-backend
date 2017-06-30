# coding: utf-8
from __future__ import unicode_literals
from django.core.management.base import BaseCommand
from escuelas import models

import requests

BASE_URL = 'http://suite-api.dtelab.com.ar/api/'

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

        self.importar_escuelas()
        self.importar_contactos()
        self.importar_pisos()

    def crear_regiones(self):
        numeros = range(1, 26)

        for n in numeros:
            p, created = models.Region.objects.get_or_create(numero=n)
            print(p)

        p, created = models.Region.objects.get_or_create(numero=27)
        print(p)

    def importar_distritos_y_localidades(self):
        localidades = self.obtener_datos_desde_api('localidades')['localidades']

        for localidad in localidades:
            objeto_distrito, created = models.Distrito.objects.get_or_create(nombre=localidad['distrito'].title())
            objeto_localidad, created = models.Localidad.objects.get_or_create(nombre=localidad['localidad'].title())

            objeto_localidad.distrito = objeto_distrito
            objeto_localidad.save()

            objeto_distrito.region, created = models.Region.objects.get_or_create(numero=int(localidad['region']))
            objeto_distrito.save()

            print objeto_distrito, " -> ", objeto_localidad, "de la", objeto_distrito.region

    def importar_escuelas(self):
        escuelas = self.obtener_datos_desde_api('escuelas')['escuelas']

        for escuela in escuelas:
            print "Intentando crear el registro escuela id_original:", escuela['id']

            objeto_escuela, created = models.Escuela.objects.get_or_create(nombre=escuela['nombre'].title())
            objeto_area, created = models.Area.objects.get_or_create(nombre=escuela['area'].title())
            objeto_localidad, created = models.Localidad.objects.get_or_create(nombre=escuela['localidad'].title())
            objeto_tipoDeFinanciamiento, created = models.TipoDeFinanciamiento.objects.get_or_create(nombre=escuela['tipo_financiamiento'].title())
            objeto_nivel, created = models.Nivel.objects.get_or_create(nombre=escuela['nivel'].title())
            objeto_tipoDeGestion, created = models.TipoDeGestion.objects.get_or_create(nombre=escuela['tipo_gestion'].title())
            #objeto_programa, created = models.Programa.objects.get_or_create(nombre=escuela['programa'].title())

            objeto_escuela.cue = escuela['cue']
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



            #print " Escuela ", objeto_escuela
            print "Se ha creado el registro:"
            print objeto_escuela, "\n CUE: ", objeto_escuela.cue, "\n Direccion: ", objeto_escuela.direccion, "\n Tel: ", objeto_escuela.telefono, "\n ", objeto_escuela.localidad, "\n ", objeto_escuela.area, "\n ", objeto_escuela.nivel, "\n ", objeto_escuela.tipoDeFinanciamiento, "\n ", objeto_escuela.tipoDeGestion
            print "==========="
            #, "\n Programa: ", objeto_escuela.programas

    def importar_contactos(self):
        contactos = self.obtener_datos_desde_api('contactos')['contactos']

        for contacto in contactos:
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

            print "Se ha creado el registro:"
            print "Nombre: ", objeto_contacto, "\n Teléfono Particular ", objeto_contacto.telefono_particular, "\n Teléfono Celular: ", objeto_contacto.telefono_celular, "\n Email: ", objeto_contacto.email, "\n Horario: ", objeto_contacto.horario
            print "==========="

    def importar_pisos(self):
        pisos = self.obtener_datos_desde_api('pisos')['pisos']

        for piso in pisos:
            print "Busando piso para escuela: ", piso['cue']
            objeto_escuela = models.Escuela.objects.get(cue=piso['cue'])
            objeto_piso, created = models.Piso.objects.get_or_create(servidor=piso['marca'])
            #
            objeto_piso.serie = piso['serie']

            if piso['ups']:
                if piso['ups'] == "SI":
                    objeto_piso.ups = 1
                else:
                    objeto_piso.ups = 0

            if piso['rack']:
                if piso['rack'] == "SI":
                    objeto_piso.rack = 1
                else:
                    objeto_piso.rack = 0

            objeto_piso.estado = piso['estado']

            objeto_escuela.piso = objeto_piso

            objeto_piso.save()
            objeto_escuela.save()

            print "Se ha creado el registro:"
            print "Piso de escuela ", piso['cue'], ": \n Servidor: ", piso['marca'], "\n Serie: ", piso['serie'], "\n UPS: ", piso['ups'], "\n Rack: ", piso['rack'], "\n Estado: ", piso['piso_estado']
            print "==========="

    def obtener_datos_desde_api(self, data):
        url = BASE_URL + data
        print("Consultando la URL: " + url)
        resultado = requests.get(url)
        return resultado.json()

    def crear_tipos_de_financiamiento(self):
        nombres = ["Nacional", "Provincial", "Municipal", "Propio"]

        for nombre in nombres:
            p, created = models.TipoDeFinanciamiento.objects.get_or_create(nombre=nombre)
            print(p)

    def crear_niveles(self):
        nombres = ["Inicial", "Primaria", "Secundaria", "Superior"]

        for nombre in nombres:
            p, created = models.Nivel.objects.get_or_create(nombre=nombre)
            print(p)

    def crear_tipos_de_gestion(self):
        nombres = ["Estatal", "Privada", "Compartida"]

        for nombre in nombres:
            p, created = models.TipoDeGestion.objects.get_or_create(nombre=nombre)
            print(p)

    def crear_areas(self):
        nombres = ["Urbana", "Rural"]

        for nombre in nombres:
            p, created = models.Area.objects.get_or_create(nombre=nombre)
            print(p)

    def crear_programas(self):
        nombres = [
            "Conectar Igualdad",
            "PAD",
            "Responsabilidad Empresarial",
            "Primaria Digital",
            "Escuelas del Futuro"
            ]

        for nombre in nombres:
            p, created = models.Programa.objects.get_or_create(nombre=nombre)
            print(p)

    def crear_experiencias(self):
        nombres = [
            "Técnico",
            "Pedagógico",
            "Administrativo",
            "Diseño",
            "Comunicación"
            ]

        for nombre in nombres:
            p, created = models.Experiencia.objects.get_or_create(nombre=nombre)
            print(p)

    def crear_contratos(self):
        nombres = [
            "PLANIED",
            "Planta/PLANIED",
            "Planta",
            "ConIg",
            "Ord. Tec."

            ]

        for nombre in nombres:
            p, created = models.Contrato.objects.get_or_create(nombre=nombre)
            print(p)

    def crear_cargos(self):
        nombres = [
            ("FED", "Facilitador Educación Digital"),
            ("Coord", "Coordinador")
            ]

        for nombre in nombres:
            p, created = models.Cargo.objects.get_or_create(nombre=nombre[0], descripcion=nombre[1])
            print(p)

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

        for nombre in nombres:
            p, created = models.CargoEscolar.objects.get_or_create(nombre=nombre)
            print(p)
