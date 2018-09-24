# coding: utf-8
from __future__ import unicode_literals
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime
from datetime import date
import json

class EventoDeRobotica(models.Model):
    OPCIONES_SI_NO = (
        ('Si', 'Si'),
        ('No', 'No'),
    )
    escuela = models.ForeignKey('Escuela', on_delete=models.CASCADE, related_name='eventos_de_robotica', default=None, blank=True, null=True)

    tallerista = models.ForeignKey('Perfil', on_delete=models.CASCADE, related_name='tallerista_eventos_de_robotica', default=None, blank=True, null=True)

    titulo = models.ForeignKey('TallerDeRobotica', on_delete=models.CASCADE, related_name='titulo_eventos_de_robotica', default=None, blank=True, null=True)

    curso = models.ForeignKey('CursoDeRobotica', on_delete=models.CASCADE, related_name='curso_eventos_de_robotica', default=None, blank=True, null=True)
    seccion = models.ForeignKey('SeccionDeRobotica', on_delete=models.CASCADE, related_name='seccion_eventos_de_robotica', default=None, blank=True, null=True)

    cantidad_de_alumnos = models.IntegerField(default=None, blank=True, null=True)

    docente_a_cargo = models.CharField(max_length=512, default=None, blank=True, null=True)

    area_en_que_se_dicta = models.ForeignKey('AreaDeRobotica', on_delete=models.CASCADE, related_name='area_eventos_de_robotica', default=None, blank=True, null=True)

    fecha = models.DateField(default=date.today)
    inicio = models.TimeField(default=datetime.now)
    fin = models.TimeField(default=datetime.now)

    minuta = models.TextField(max_length=4096, default=None, blank=True, null=True)

    acta = models.FileField(default=None, blank=True, null=True)

    cerrar_evento = models.BooleanField(default=False)

    se_dio_el_taller = models.CharField(max_length=3, choices=OPCIONES_SI_NO, default=None, blank=True, null=True)
    motivo = models.TextField(max_length=512, default=None, blank=True, null=True)

    fecha_de_ultima_modificacion = models.DateTimeField(auto_now=True)
    fecha_de_creacion = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.titulo.nombre

    class Meta:
        db_table = 'eventos_de_robotica'
        verbose_name_plural = "Eventos (Robotica)"
        ordering = ('-fecha',)

    def resumenParaCalendario(self):
        titulo = self.titulo.nombre
        escuela = self.escuela.nombre
        region = self.escuela.localidad.distrito.region.numero
        localidad = self.escuela.localidad.nombre
        distrito = self.escuela.localidad.distrito.nombre
        tallerista = self.tallerista.nombre + " " + self.tallerista.apellido
        inicio = self.inicio.strftime("%H:%M")
        fin = self.fin.strftime("%H:%M")
        resumen = json.dumps(
                {
                    "titulo": titulo,
                    "escuela": escuela,
                    "region": region,
                    "localidad": localidad,
                    "distrito": distrito,
                    "inicio": inicio,
                    "fin": fin,
                    "tallerista": tallerista
                },ensure_ascii=False)
        if resumen:
            return json.loads(resumen)
        else:
            return "Sin resumen"

    def esDelEquipoRegion(self, numero_de_region):
        if self.tallerista.region.numero is int(numero_de_region):
            return True

        return False

    def puedeSerEditadaPor(self, perfil):
        "Indica si un taller puede ser editado por un perfil en particular."

        # Sin importar el perfil, el evento no se tiene que poder editar
        # si tiene acta. Excepto administrador, que puede editar aún cerrado.
        if self.cerrar_evento == True:
            if perfil.group.name =="Administrador":
                return True
            else:
                return False

        # Si es responsable tiene que poder editarlo.
        if perfil == self.tallerista:
            return True

        # Si el perfil es Admin, puede editar el taller
        if perfil.group.name == "Administrador":
            return True

        return False

@receiver(post_save, sender=EventoDeRobotica)
def create_event_summary(sender, instance, created, **kwargs):
    post_save.disconnect(create_event_summary, sender=sender)

    tallerista = instance.tallerista.nombre + " " + instance.tallerista.apellido
    escuela = instance.escuela.nombre
    titulo = instance.titulo.nombre
    region = instance.escuela.localidad.distrito.region

    resumen = json.dumps(
            {
                "titulo": titulo,
                "escuela": escuela,
                "tallerista": tallerista
            },ensure_ascii=False)

    instance.resumen = resumen
    instance.save()

    post_save.connect(create_event_summary, sender=sender)
