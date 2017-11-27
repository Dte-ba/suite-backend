# coding: utf-8
from django.db import models

class Region(models.Model):
    numero = models.IntegerField()

    def __unicode__(self):
        return str(self.numero)

    class Meta:
        db_table = 'regiones'
        verbose_name_plural = "regiones"

    class JSONAPIMeta:
        resource_name = 'regiones'
