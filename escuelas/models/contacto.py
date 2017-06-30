# coding: utf-8
from django.db import models

class Contacto(models.Model):
    nombre = models.CharField(max_length=200)
    telefono_particular = models.CharField(max_length=100)
    telefono_celular = models.CharField(max_length=100)
    horario = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)

    escuela = models.ForeignKey('Escuela', related_name='contactos', on_delete=models.CASCADE)
    cargo = models.ForeignKey('CargoEscolar', related_name='contactos', on_delete=models.CASCADE, default=None, blank=True, null=True)

    def __unicode__(self):
        return self.nombre

    class Meta:
        db_table = 'contactos'
        verbose_name_plural = "contactos"
