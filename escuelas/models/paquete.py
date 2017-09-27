# coding: utf-8
from django.db import models

class Paquete(models.Model):
    legacy_id = models.IntegerField(default=None, blank=True, null=True)
    escuela = models.ForeignKey('Escuela', on_delete=models.CASCADE, related_name='paquetes', default=None, blank=True, null=True)
    fecha_pedido = models.DateField(default=None, blank=True, null=True)
    ne = models.CharField(max_length=512, default=None, blank=True, null=True)
    id_hardware = models.CharField(max_length=512, default=None, blank=True, null=True)
    marca_de_arranque = models.CharField(max_length=512, default=None, blank=True, null=True)
    comentario = models.TextField(max_length=1024, default=None, blank=True, null=True)
    carpeta_paquete = models.CharField(max_length=512, default=None, blank=True, null=True)
    fecha_envio = models.DateField(default=None, blank=True, null=True) # Fecha en que se mandó el pedido a Educar
    zip_paquete = models.CharField(max_length=512, default=None, blank=True, null=True) # Zip con pedido y llaves que se envía por mail a Educar
    estado = models.ForeignKey('EstadoDePaquete', on_delete=models.CASCADE, related_name='paquetes', default=None, blank=True, null=True)
    fecha_devolucion = models.DateField(default=None, blank=True, null=True) # Fecha en que se recibió el paquete solicitado desde Educar
    id_devolucion = models.IntegerField(default=None, blank=True, null=True) # ID que se relaciona con la tabla devoluciones (legacy)
    leido = models.BooleanField(default=False)
    tpmdata = models.BooleanField(default=False)

    def __unicode__(self):
        return str(self.legacy_id)

    class Meta:
        db_table = 'paquetes'
        verbose_name_plural = "paquetes"
        ordering = ('-fecha_pedido',)

    class JSONAPIMeta:
        resource_name = 'paquetes'
