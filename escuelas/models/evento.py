# coding: utf-8
from django.db import models

class Evento(models.Model):
    legacy_id = models.IntegerField(default=None, blank=True, null=True)

    titulo = models.CharField(max_length=512)
    fecha = models.DateField(default='2017-01-10')
    fecha_fin = models.DateField(default='2017-01-10')
    inicio = models.TimeField(default='00:00:00')
    fin = models.TimeField(default='00:00:00')
    todoElDia = models.BooleanField(default=False)

    responsable = models.ForeignKey('Perfil', on_delete=models.CASCADE, related_name='eventos', default=None, blank=True, null=True)
    escuela = models.ForeignKey('Escuela', on_delete=models.CASCADE, related_name='eventos', default=None, blank=True, null=True)

    def __unicode__(self):
        return self.titulo

    class Meta:
        db_table = 'eventos'
        verbose_name_plural = "eventos"
