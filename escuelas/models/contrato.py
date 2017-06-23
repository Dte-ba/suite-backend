# coding: utf-8
from django.db import models

class Contrato(models.Model):
    nombre = models.CharField(max_length=255)

    def __unicode__(self):
        return u"Contrato: " + self.nombre

    class Meta:
        db_table = 'contratos'
        verbose_name_plural = 'contratos'

    class JSONAPIMeta:
        resource_name = "contratos"
