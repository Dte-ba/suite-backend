# coding: utf-8
from __future__ import unicode_literals
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models.signals import post_save
import json

REGIONES = (
    (0, u'Sin definir'),
    (1, u'Región 1'),
    (2, u'Región 2'),
    (3, u'Región 3'),
    (4, u'Región 4'),
    (5, u'Región 5'),
    (6, u'Región 6'),
    (7, u'Región 7'),
    (8, u'Región 8'),
    (9, u'Región 9'),
    (10, u'Región 10'),
    (11, u'Región 11'),
    (12, u'Región 12'),
    (13, u'Región 13'),
    (14, u'Región 14'),
    (15, u'Región 15'),
    (16, u'Región 16'),
    (17, u'Región 17'),
    (18, u'Región 18'),
    (19, u'Región 19'),
    (20, u'Región 20'),
    (21, u'Región 21'),
    (22, u'Región 22'),
    (23, u'Región 23'),
    (24, u'Región 24'),
    (25, u'Región 25'),
    (26, u'Región 26'),
    (27, u'Región 27'),
)

class Evento(models.Model):
    legacy_id = models.IntegerField(default=None, blank=True, null=True)

    titulo = models.CharField(max_length=512)
    fecha = models.DateField(default='2017-01-10')
    fecha_fin = models.DateField(default='2017-01-10')
    inicio = models.TimeField(default='00:00:00')
    fin = models.TimeField(default='00:00:00')
    region = models.IntegerField(default=0, choices=REGIONES)

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

    fecha_de_ultima_modificacion = models.DateTimeField(auto_now=True)
    fecha_de_creacion = models.DateTimeField(auto_now_add=True)


    def __unicode__(self):
        return self.titulo

    class Meta:
        db_table = 'eventos'
        verbose_name_plural = "eventos"
        ordering = ('-fecha',)

    def resumenParaCalendario(self):
        titulo = self.titulo
        categoria = self.categoria.nombre
        escuela = self.escuela.nombre
        cue = self.escuela.cue
        traslado = self.requiere_traslado
        region = self.escuela.localidad.distrito.region.numero
        localidad = self.escuela.localidad.nombre
        distrito = self.escuela.localidad.distrito.nombre
        responsable = self.responsable.nombre + " " + self.responsable.apellido
        inicio = self.fecha.strftime("%d/%m/%Y") + " a las " + self.inicio.strftime("%H:%M")
        fin = self.fecha_fin.strftime("%d/%m/%Y") + " a las " + self.fin.strftime("%H:%M")
        resumen = json.dumps(
                {
                    "titulo": titulo,
                    "categoria": categoria,
                    "escuela": escuela,
                    "cue": cue,
                    "region": region,
                    "localidad": localidad,
                    "distrito": distrito,
                    "inicio": inicio,
                    "fin": fin,
                    "responsable": responsable,
                    "traslado": traslado
                },ensure_ascii=False)
        if resumen:
            return json.loads(resumen)
        else:
            return "Sin resumen"

    def esDelEquipoRegion(self, numero_de_region):
        if self.region is int(numero_de_region):
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

@receiver(post_save, sender=Evento)
def asignar_numero_de_region(sender, instance, created, **kwargs):
    post_save.disconnect(asignar_numero_de_region, sender=Evento)

    if instance.region == 0:
        if instance.responsable and instance.responsable.region and instance.responsable.region.numero == 27:
            instance.region = 27
        else:
            if instance.escuela and instance.escuela.cue != "60000000":
                instance.region = instance.escuela.numero_de_region()
            else:
                if instance.responsable and instance.responsable.region:
                    instance.region = instance.responsable.region.numero

    instance.save()
    post_save.connect(asignar_numero_de_region, sender=Evento)
