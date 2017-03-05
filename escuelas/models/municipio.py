# coding: utf-8
from django.db import models

class Municipio(models.Model):
    numero = models.CharField(max_length=10)
    nombre = models.CharField(max_length=255)
    region = models.ForeignKey('Region', on_delete=models.CASCADE, related_name='municipios')

    def __unicode__(self):
        return self.nombre

    class Meta:
        db_table = 'municipios'
        verbose_name_plural = 'municipios'
