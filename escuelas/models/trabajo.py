# coding: utf-8
from __future__ import unicode_literals
from django.db import models
from django.core.exceptions import ObjectDoesNotExist


class Trabajo(models.Model):
    fecha = models.DateTimeField(auto_now=True)
    trabajo_id = models.CharField(max_length=128)
    nombre = models.CharField(max_length=256)
    detalle = models.TextField(max_length=2048, default=u"", blank=True, null=True)
    archivo = models.FileField(default=None, blank=True, null=True)
    resultado = models.TextField(max_length=512, default=None, blank=True, null=True)
    progreso = models.IntegerField(default=0, blank=True, null=True)

    class Meta:
        ordering = ('-fecha',)

    def actualizar_paso(self, paso, cantidad_de_pasos, detalle):
        self.progreso = int((paso / float(cantidad_de_pasos)) * 100)
        self.detalle += detalle + u"\n"
        self.save()

    @classmethod
    def obtener_desde_trabajo_id(kls, trabajo_id):
        try:
            return Trabajo.objects.get(trabajo_id=trabajo_id)
        except ObjectDoesNotExist:
            return None
