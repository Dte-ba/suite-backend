# coding: utf-8
from django.db import models

class Experiencia(models.Model):
    nombre = models.CharField(max_length=255)

    def __unicode__(self):
        return u"Experiencia: " + self.nombre

    class Meta:
        db_table = 'experiencias'
        verbose_name_plural = 'experiencias'

    class JSONAPIMeta:
        resource_name = "experiencias"
