# coding: utf-8
from django.db import models

class Tarea(models.Model):
    id_ticket_original = models.IntegerField() # Para historico de SUITE Legacy
    titulo = models.CharField(max_length=200)
    fechaDeAlta = models.DateField(default=None, blank=True,null=True)
    autor = models.ForeignKey('Perfil', related_name='tareas_autor', default=None, blank=True, null=True) #usuario creador de la Tarea
    responsable = models.ForeignKey('Perfil', related_name='tareas_responsable', default=None, blank=True, null=True)# Responsable Asignado
    descripcion = models.TextField(max_length=1024)
    motivo = models.ForeignKey('MotivoTarea', related_name='tareas', on_delete=models.CASCADE, default=None, blank=True, null=True)
    estado = models.ForeignKey('EstadoTarea', related_name='tareas', on_delete=models.CASCADE, default=None, blank=True, null=True)
    prioridad = models.ForeignKey('PrioridadTarea', related_name='tareas', on_delete=models.CASCADE, default=None, blank=True, null=True)

    escuela = models.ForeignKey('Escuela', related_name='tareas', on_delete=models.CASCADE, default=None, blank=True, null=True)

    def __unicode__(self):
        return self.titulo

    class Meta:
        db_table = 'tareas'
        verbose_name_plural = "tareas"

    class JSONAPIMeta:
        resource_name = 'tareas'
