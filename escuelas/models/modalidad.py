# coding: utf-8
from django.db import models

class Modalidad(models.Model):
    nombre = models.CharField(max_length=255)

    def __unicode__(self):
        return u"Modalidad: " + self.nombre

    class Meta:
        db_table = 'modalidades'
        verbose_name_plural = 'modalidades'

    class JSONAPIMeta:
        resource_name = "modalidades"
