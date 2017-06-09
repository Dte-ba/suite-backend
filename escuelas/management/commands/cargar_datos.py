from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from escuelas import models

class Command(BaseCommand):
    help = 'Genera todos los datos iniciales.'

    def handle(self, *args, **options):
        self.crear_tipos_de_financiamiento()
        self.crear_niveles()
        self.crear_tipos_de_gestion()

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
