from django.core.management.base import BaseCommand
from escuelas import models

import requests

BASE_URL = 'http://suite-api.dtelab.com.ar/api/'

class Command(BaseCommand):
    help = 'Genera todos los datos iniciales.'

    def handle(self, *args, **options):
        self.importar_distritos_y_localidades()

        self.crear_regiones()
        self.crear_tipos_de_financiamiento()
        self.crear_niveles()
        self.crear_tipos_de_gestion()
        self.crear_areas()
        self.crear_programas()

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
