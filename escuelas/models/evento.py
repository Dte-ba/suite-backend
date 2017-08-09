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

    objetivo = models.TextField(max_length=4096, default=None, blank=True, null=True)

    responsable = models.ForeignKey('Perfil', on_delete=models.CASCADE, related_name='eventos', default=None, blank=True, null=True)
    escuela = models.ForeignKey('Escuela', on_delete=models.CASCADE, related_name='eventos', default=None, blank=True, null=True)
    acompaniantes = models.ManyToManyField('Perfil', related_name='eventos_acompaniantes', default=None, blank=True)

    cantidadDeParticipantes = models.CharField(max_length=256,default=None, blank=True, null=True)
    requiereTraslado = models.BooleanField(default=False)

    def __unicode__(self):
        return self.titulo

    class Meta:
        db_table = 'eventos'
        verbose_name_plural = "eventos"
