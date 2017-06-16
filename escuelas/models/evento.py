# coding: utf-8
from django.db import models

class Evento(models.Model):
    titulo = models.CharField(max_length=512)
    fechainicio = models.DateTimeField()
    fechafin = models.DateTimeField()
    todoElDia = models.BooleanField(default=False)

    def __unicode__(self):
        return self.titulo

    class Meta:
        db_table = 'eventos'
        verbose_name_plural = "eventos"
