# coding: utf-8
from django.db import models

class Evento(models.Model):
    titulo = models.CharField(max_length=512)
    fechainicio = models.DateField()
    fechafin = models.DateField()

    def __unicode__(self):
        return self.nombre

    class Meta:
        db_table = 'eventos'
        verbose_name_plural = "eventos"
