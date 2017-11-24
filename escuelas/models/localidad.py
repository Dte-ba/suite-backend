# coding: utf-8
from django.db import models

class Localidad(models.Model):
    nombre = models.CharField(max_length=255)
    distrito = models.ForeignKey('Distrito', on_delete=models.CASCADE, related_name='localidades', default=None, blank=True, null=True)

    def cantidad_de_escuelas(self):
        return self.escuelas.count()

    def cantidad_de_perfiles_con_domicilio_vinculado(self):
        return self.perfiles.count()

    def __unicode__(self):
        return u"Localidad: " + self.nombre

    class Meta:
        db_table = 'localidades'
        verbose_name_plural = 'localidades'

    class JSONAPIMeta:
        resource_name = "localidades"

    def numero_de_region(self):
        return self.distrito.region.numero
