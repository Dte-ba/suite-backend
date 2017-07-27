# coding: utf-8
from django.db import models

class ComentarioDeTarea(models.Model):
    tarea = models.ForeignKey('Tarea', related_name='comentariosDeTarea', default=None, blank=True, null=True) # Para historico de SUITE Legacy
    fechaDeAlta = models.DateField(default=None, blank=True,null=True)
    autor = models.ForeignKey('Perfil', related_name='comentarios_tarea_autor', default=None, blank=True, null=True) #usuario creador del comentario
    comentario = models.TextField(max_length=4096, default=None, blank=True, null=True)


    def __unicode__(self):
        return str(self.tarea)

    class Meta:
        db_table = 'comentariosDeTareas'
        verbose_name_plural = "comentariosDetareas"
