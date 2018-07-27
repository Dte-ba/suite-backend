# coding: utf-8
from django.db import models

class Aplicacion(models.Model):
    nombre = models.CharField(max_length=255)

    def __unicode__(self):
        return u"App: " + self.nombre

    class Meta:
        db_table = 'aplicaciones'
        verbose_name_plural = 'aplicaciones'

    class JSONAPIMeta:
        resource_name = 'aplicaciones'
