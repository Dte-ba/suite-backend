# coding: utf-8
from django.db import models

class TipoDeFinanciamiento(models.Model):
    nombre = models.CharField(max_length=255)

    def __unicode__(self):
        return u"TipoDeFinanciamiento: %s" %(self.nombre)

    class Meta:
        db_table = 'tiposDeFinanciamiento'
        verbose_name_plural = 'tiposDeFinanciamiento'

    class JSONAPIMeta:
        resource_name = "tipos-de-financiamiento"
