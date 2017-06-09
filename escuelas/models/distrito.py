# coding: utf-8
from django.db import models

class Distrito(models.Model):
    nombre = models.CharField(max_length=255)

    def __unicode__(self):
        return u"Distrito: " + self.nombre

    class Meta:
        db_table = 'distritos'
        verbose_name_plural = 'distritos'

    class JSONAPIMeta:
        resource_name = "distritos"
