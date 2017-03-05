# coding: utf-8
from django.db import models

class Perfil(models.Model):
    nombre = models.CharField(max_length=200)
    apellido = models.CharField(max_length=200)
    dni = models.CharField(max_length=200)
    cuit = models.CharField(max_length=200)
    fechadenacimiento = models.DateField()

    def __unicode__(self):
        return self.dni

    class Meta:
        db_table = 'perfiles'
        verbose_name_plural = "perfiles"
