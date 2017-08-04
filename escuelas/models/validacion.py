# coding: utf-8
from django.db import models

class Validacion(models.Model):
    legacy_id = models.IntegerField(default=None, blank=True, null=True) # Para historico de SUITE Legacy

    fechaDeAlta = models.DateField(default=None, blank=True,null=True)
    autor = models.ForeignKey('Perfil', related_name='validaciones', default=None, blank=True, null=True) #usuario creador de la validacion
    cantidad = models.CharField(max_length=255, default=None, blank=True, null=True)
    observaciones = models.TextField(max_length=1024)

    estado = models.ForeignKey('EstadoDeValidacion', related_name='validaciones', on_delete=models.CASCADE, default=None, blank=True, null=True)


    escuela = models.ForeignKey('Escuela', related_name='validaciones', on_delete=models.CASCADE, default=None, blank=True, null=True)

    def __unicode__(self):
        return str(self.fechaDeAlta)

    class Meta:
        db_table = 'validaciones'
        verbose_name_plural = "validaciones"

    class JSONAPIMeta:
        resource_name = 'validaciones'
