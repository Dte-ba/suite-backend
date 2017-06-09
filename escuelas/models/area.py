# coding: utf-8
from django.db import models

class Area(models.Model):
    nombre = models.CharField(max_length=255)

    def __unicode__(self):
        return u"Area: " + self.nombre

    class Meta:
        db_table = 'areas'
        verbose_name_plural = 'areas'

    class JSONAPIMeta:
        resource_name = "areas"
