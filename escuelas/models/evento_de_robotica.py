# coding: utf-8
from __future__ import unicode_literals
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
import json

class EventoRobotica(models.Model):

    escuela = models.ForeignKey('Escuela', on_delete=models.CASCADE, related_name='eventos_de_robotica', default=None, blank=True, null=True)
    # cue, region, distrito y telefono salen de los datos de escuela.

    #nombre_del_directivo #Sale de la escuela o es un campo propio del evento?
    #correo_electronico #Es el de la escuela o el del directivo

    tallerista = models.ForeignKey('Perfil', on_delete=models.CASCADE, related_name='tallerista_eventos_de_robotica', default=None, blank=True, null=True)

    # coordinador = models.ForeignKey('Perfil', on_delete=models.CASCADE, related_name='coordinador_eventos_de_robotica', default=None, blank=True, null=True) # Se asigna o sale automáticamente por tallerista o escuela/region?

    #titulo = # Campo de texto o modelo

    #curso / seccion

    cantidad_de_alumnos = models.IntegerField(default=None, blank=True, null=True)

    docente_a_cargo = models.CharField(max_length=512, default=None, blank=True, null=True)

    #area_en_que_se_dicta = # Campo de texto o modelo

    fecha = models.DateField(default=datetime.date.today)
    fecha_fin = models.DateField(default=datetime.date.today)
    inicio = models.TimeField(default=datetime.date.now)
    fin = models.TimeField(default=datetime.date.now)

    categoria = models.ForeignKey('CategoriaDeEventoRobotica', on_delete=models.CASCADE, related_name='eventos', default=None, blank=True, null=True)
    objetivo = models.TextField(max_length=4096, default=None, blank=True, null=True)

    acta = models.FileField(default=None, blank=True, null=True)

    def __unicode__(self):
        return self.titulo

    class Meta:
        db_table = 'eventos_de_robotica'
        verbose_name_plural = "eventos_de_robotica"
        ordering = ('-fecha',)

    def resumenParaCalendario(self):
        if self.resumen:
            return json.loads(self.resumen)
        else:
            return "Sin resumen"

    def esDelEquipoRegion(self, numero_de_region):
        if self.tallerista.region.numero is int(numero_de_region):
            return True

        return False


@receiver(post_save, sender=EventoRobotica)
def create_event_summary(sender, instance, created, **kwargs):
    post_save.disconnect(create_event_summary, sender=sender)

    tallerista = instance.tallerista.nombre + " " + instance.tallerista.apellido
    escuela = instance.escuela.nombre
    # titulo = instance.titulo
    region = instance.escuela.localidad.distrito.region

    resumen = json.dumps(
            {
                "titulo": titulo,
                "categoria": categoria.nombre,
                "region": region.numero,
                "escuela": escuela,
                "tallerista": tallerista
            },ensure_ascii=False)

    instance.resumen = resumen
    instance.save()

    post_save.connect(create_event_summary, sender=sender)
