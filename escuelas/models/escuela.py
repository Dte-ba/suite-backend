# coding: utf-8
from django.db import models

class Escuela(models.Model):
    cue = models.CharField(max_length=8, db_index=True)
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255, default=None, blank=True, null=True)
    latitud = models.CharField(max_length=15, default=None, blank=True, null=True)
    longitud = models.CharField(max_length=15, default=None, blank=True, null=True)
    localidad = models.ForeignKey('Localidad', on_delete=models.CASCADE, related_name='escuelas', default=None, blank=True, null=True)
    tipoDeFinanciamiento = models.ForeignKey('TipoDeFinanciamiento', on_delete=models.CASCADE, related_name='escuelas', default=None, blank=True, null=True)
    nivel = models.ForeignKey('Nivel', on_delete=models.CASCADE, related_name='escuelas', default=None, blank=True, null=True)
    tipoDeGestion = models.ForeignKey('TipoDeGestion', on_delete=models.CASCADE, related_name='escuelas', default=None, blank=True, null=True)
    area = models.ForeignKey('Area', on_delete=models.CASCADE, related_name='escuelas', default=None, blank=True, null=True)
    programa = models.ForeignKey('Programa', on_delete=models.CASCADE, related_name='escuelas', default=None, blank=True, null=True)


    def __unicode__(self):
        return self.nombre

    class Meta:
        db_table = 'escuelas'
        verbose_name_plural = "escuelas"
