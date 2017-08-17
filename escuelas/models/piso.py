# coding: utf-8
from django.db import models

def upload_to(filename):
    return 'piso_llave_servidor/{0}'.format(filename)

class Piso(models.Model):
    legacy_id = models.IntegerField(default=None, blank=True, null=True) # Para historico de SUITE Legacy
    servidor = models.CharField(max_length=255, default=None, blank=True, null=True)
    serie = models.CharField(max_length=255, default=None, blank=True, null=True)
    ups = models.BooleanField(default=False)
    rack = models.BooleanField(default=False)
    estado = models.BooleanField(default=False)
    llave = models.FileField(upload_to='piso_llave_servidor/', blank=True, null=True)

    class Meta:
        db_table = 'pisos'
        verbose_name_plural = 'pisos'

    class JSONAPIMeta:
        resource_name = "pisos"
