# coding: utf-8
from django.db import models

class MotivoDeConformacion(models.Model):
    nombre = models.CharField(max_length=255)

    def __unicode__(self):
        return u"Motivo: " + self.nombre

    class Meta:
        db_table = 'motivosDeConformacion'
        verbose_name_plural = 'motivosDeConformacion'
