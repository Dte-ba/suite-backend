# coding: utf-8
from django.db import models

class Nivel(models.Model):
    nombre = models.CharField(max_length=255)

    def __unicode__(self):
        return self.nombre

    class Meta:
        db_table = 'niveles'
        verbose_name_plural = 'niveles'

    class JSONAPIMeta:
        resource_name = "niveles"
