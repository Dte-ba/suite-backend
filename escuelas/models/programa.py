# coding: utf-8
from django.db import models

class Programa(models.Model):
    nombre = models.CharField(max_length=255)

    def __unicode__(self):
        return u"Programa: " + self.nombre

    class Meta:
        db_table = 'programas'
        verbose_name_plural = 'programas'

    class JSONAPIMeta:
        resource_name = "programas"
