from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from escuelas import models

import requests

class Command(BaseCommand):
    help = 'Genera todos los datos iniciales.'

    def handle(self, *args, **options):
        self.importar_usuarios()

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

    def importar_usuarios(self):
        #print(self.obtener_datos_desde_api('usuarios/'))
        pass

    def obtener_datos_desde_api(self, data):
        url = 'http://suite.dtelab.com.ar/suite/datasuite/api/' + data
        return requests.get(url).json()

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
