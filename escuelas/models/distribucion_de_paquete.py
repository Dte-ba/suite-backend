# coding: utf-8
from __future__ import unicode_literals
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class DistribucionDePaquete(models.Model):
    fecha = models.DateTimeField(auto_now=True)
    archivo = models.FileField(default=None, blank=True, null=True)

    class Meta:
        db_table = 'distribucion_de_paquete'
        verbose_name_plural = "distribucionDePaquetes"
        ordering = ('-fecha',)

    class JSONAPIMeta:
        resource_name = "distribucion-de-paquetes"
