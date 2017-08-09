# coding: utf-8
from django.db import models

class ComentarioDeValidacion(models.Model):
    legacy_id = models.IntegerField(default=None, blank=True, null=True) # Para historico de SUITE Legacy
    validacion = models.ForeignKey('Validacion', related_name='comentariosDeValidacion', default=None, blank=True, null=True)
    fecha = models.DateField(default=None, blank=True,null=True)
    autor = models.ForeignKey('Perfil', related_name='comentariosDeValidacion', default=None, blank=True, null=True) #usuario creador del comentario
    comentario = models.TextField(max_length=4096, default=None, blank=True, null=True)
    cantidad = models.CharField(max_length=255, default=None, blank=True, null=True)


    def __unicode__(self):
        return "Comentario de la validacion " + str(self.validacion)

    class Meta:
        db_table = 'comentariosDeValidacion'
        verbose_name_plural = "comentariosDeValidacion"
