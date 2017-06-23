# coding: utf-8
from django.db import models

class Piso(models.Model):
    servidor = models.CharField(max_length=255)
    serie = models.CharField(max_length=255)
    ups = models.BooleanField()
    rack = models.BooleanField()
    estado = models.BooleanField()

    def __unicode__(self):
        return u"Piso: " + self.servidor + " Serie " + self.serie

    class Meta:
        db_table = 'pisos'
        verbose_name_plural = 'pisos'

    class JSONAPIMeta:
        resource_name = "pisos"
