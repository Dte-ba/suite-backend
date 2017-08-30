# coding: utf-8
from __future__ import unicode_literals
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
import json

class Evento(models.Model):
    legacy_id = models.IntegerField(default=None, blank=True, null=True)

    titulo = models.CharField(max_length=512)
    fecha = models.DateField(default='2017-01-10')
    fecha_fin = models.DateField(default='2017-01-10')
    inicio = models.TimeField(default='00:00:00')
    fin = models.TimeField(default='00:00:00')
    todoElDia = models.BooleanField(default=False)

    categoria = models.ForeignKey('CategoriaDeEvento', on_delete=models.CASCADE, related_name='eventos', default=None, blank=True, null=True)
    objetivo = models.TextField(max_length=4096, default=None, blank=True, null=True)

    responsable = models.ForeignKey('Perfil', on_delete=models.CASCADE, related_name='eventos', default=None, blank=True, null=True)
    escuela = models.ForeignKey('Escuela', on_delete=models.CASCADE, related_name='eventos', default=None, blank=True, null=True)
    acompaniantes = models.ManyToManyField('Perfil', related_name='eventos_acompaniantes', default=None, blank=True)

    cantidadDeParticipantes = models.CharField(max_length=256,default=None, blank=True, null=True)
    requiereTraslado = models.BooleanField(default=False)

    resumen = models.TextField(max_length=1024, default=None, blank=True, null=True)

    def __unicode__(self):
        return self.titulo

    class Meta:
        db_table = 'eventos'
        verbose_name_plural = "eventos"

    def resumenParaCalendario(self):
        if self.resumen:
            print(self.id)
            print(self.resumen)
            return json.loads(self.resumen)
        else:
            return "Sin resumen"


@receiver(post_save, sender=Evento)
def create_event_summary(sender, instance, created, **kwargs):
    if created:
        titulo = instance.titulo
        categoria = instance.categoria

        region = instance.escuela.localidad.distrito.region
        escuela = instance.escuela.nombre
        responsable = instance.responsable.nombre + " " + instance.responsable.apellido

        resumen = json.dumps(
                {
                    "titulo": titulo,
                    "categoria": categoria.nombre,
                    "region": region.numero,
                    "escuela": escuela,
                    "responsable": responsable
                },ensure_ascii=False)

        instance.resumen = resumen
        instance.save()
