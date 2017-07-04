# coding: utf-8
from django.db import models

class Piso(models.Model):
    servidor = models.CharField(max_length=255)
    serie = models.CharField(max_length=255, default=None, blank=True, null=True)
    ups = models.BooleanField(default=False)
    rack = models.BooleanField(default=False)
    estado = models.BooleanField(default=False)

    class Meta:
        db_table = 'pisos'
        verbose_name_plural = 'pisos'

    class JSONAPIMeta:
        resource_name = "pisos"
