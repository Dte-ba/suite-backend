# coding: utf-8
from django.db import models

class Tarea(models.Model):
    id_ticket_original = models.IntegerField(default=None, blank=True, null=True) # Para historico de SUITE Legacy
    titulo = models.CharField(max_length=200)
    fecha_de_alta = models.DateField(default=None, blank=True,null=True)
    autor = models.ForeignKey('Perfil', related_name='tareas_autor', default=None, blank=True, null=True) #usuario creador de la Tarea
    responsable = models.ForeignKey('Perfil', related_name='tareas_responsable', default=None, blank=True, null=True)# Responsable Asignado
    descripcion = models.TextField(max_length=1024)
    motivo_de_tarea = models.ForeignKey('MotivoDeTarea', related_name='tareas', on_delete=models.CASCADE, default=None, blank=True, null=True)
    estado_de_tarea = models.ForeignKey('EstadoDeTarea', related_name='tareas', on_delete=models.CASCADE, default=None, blank=True, null=True)
    prioridad_de_tarea = models.ForeignKey('PrioridadDeTarea', related_name='tareas', on_delete=models.CASCADE, default=None, blank=True, null=True)

    escuela = models.ForeignKey('Escuela', related_name='tareas', on_delete=models.CASCADE, default=None, blank=True, null=True)

    def __unicode__(self):
        return self.titulo

    class Meta:
        db_table = 'tareas'
        verbose_name_plural = "tareas"

    class JSONAPIMeta:
        resource_name = 'tareas'
