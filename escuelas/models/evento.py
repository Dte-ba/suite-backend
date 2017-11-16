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

    categoria = models.ForeignKey('CategoriaDeEvento', on_delete=models.CASCADE, related_name='eventos', default=None, blank=True, null=True)
    objetivo = models.TextField(max_length=4096, default=None, blank=True, null=True)

    responsable = models.ForeignKey('Perfil', on_delete=models.CASCADE, related_name='eventos', default=None, blank=True, null=True)
    escuela = models.ForeignKey('Escuela', on_delete=models.CASCADE, related_name='eventos', default=None, blank=True, null=True)
    acompaniantes = models.ManyToManyField('Perfil', related_name='eventos_acompaniantes', default=None, blank=True)

    cantidad_de_participantes = models.CharField(max_length=256,default=None, blank=True, null=True)
    requiere_traslado = models.BooleanField(default=False)

    resumen = models.TextField(max_length=1024, default=None, blank=True, null=True)

    minuta = models.TextField(max_length=4096, default=None, blank=True, null=True)
    acta_legacy = models.CharField(max_length=512, default=None, blank=True, null=True)

    acta = models.FileField(default=None, blank=True, null=True)

    def __unicode__(self):
        return self.titulo

    class Meta:
        db_table = 'eventos'
        verbose_name_plural = "eventos"
        ordering = ('-fecha',)

    def resumenParaCalendario(self):
        if self.resumen:
            return json.loads(self.resumen)
        else:
            return "Sin resumen"

    def esDelEquipoRegion(self, numero_de_region):
        if self.responsable.region.numero is int(numero_de_region):
            return True

        for acom in self.acompaniantes.all():
            if acom.region.numero is int(numero_de_region):
                return True

        return False

    def puedeSerEditadaPor(self, perfil):
        "Indica si un evento puede ser editado por un perfil en particular."

        # Sin importar el perfil, el evento no se tiene que poder editar
        # si tiene acta.
        if self.acta_legacy or self.acta:
            return False

        # Si es responsable tiene que poder editarlo.
        if perfil == self.responsable:
            return True

        # igualmente si es un acompañate.
        if perfil in self.acompaniantes.all():
            return True

        return False


@receiver(post_save, sender=Evento)
def create_event_summary(sender, instance, created, **kwargs):
    post_save.disconnect(create_event_summary, sender=sender)

    responsable = instance.responsable.nombre + " " + instance.responsable.apellido
    escuela = instance.escuela.nombre
    categoria = instance.categoria
    titulo = instance.titulo
    region = instance.escuela.localidad.distrito.region

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

    post_save.connect(create_event_summary, sender=sender)
