# coding: utf-8
from django.db import models

class Distrito(models.Model):
    nombre = models.CharField(max_length=255)
    esCabecera = models.BooleanField(default=False)
    region = models.ForeignKey('Region', on_delete=models.CASCADE, related_name='distritos', default=None, blank=True, null=True)

    def __unicode__(self):
        return u"Distrito: " + self.nombre

    class Meta:
        db_table = 'distritos'
        verbose_name_plural = 'distritos'

    class JSONAPIMeta:
        resource_name = "distritos"

    def cantidad_de_localidades(self):
        return self.localidades.count()

    def cantidad_de_escuelas(self):
        return sum([localidad.cantidad_de_escuelas() for localidad in self.localidades.all()])

    def cantidad_de_perfiles(self):
        return sum([localidad.cantidad_de_perfiles() for localidad in self.localidades.all()])
