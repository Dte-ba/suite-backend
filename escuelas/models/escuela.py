# coding: utf-8
import datetime
from django.db import models

class Escuela(models.Model):
    cue = models.CharField(max_length=8, db_index=True)
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255, default=None, blank=True, null=True)
    telefono = models.CharField(max_length=255, default=None, blank=True, null=True)
    email = models.CharField(max_length=255, default=None, blank=True, null=True)
    latitud = models.CharField(max_length=64, default=None, blank=True, null=True)
    longitud = models.CharField(max_length=64, default=None, blank=True, null=True)
    localidad = models.ForeignKey('Localidad', related_name='escuelas', default=None, blank=True, null=True)
    tipoDeFinanciamiento = models.ForeignKey('TipoDeFinanciamiento', related_name='escuelas', default=None, blank=True, null=True)
    nivel = models.ForeignKey('Nivel', related_name='escuelas', default=None, blank=True, null=True)
    tipoDeGestion = models.ForeignKey('TipoDeGestion', related_name='escuelas', default=None, blank=True, null=True)
    area = models.ForeignKey('Area', related_name='escuelas', default=None, blank=True, null=True)
    programas = models.ManyToManyField('Programa', related_name='escuelas')
    piso = models.ForeignKey('Piso', related_name='escuelas', default=None, blank=True, null=True)

    # Para conformaciones
    padre = models.ForeignKey('self', related_name='subescuelas', on_delete=models.CASCADE, default=None, blank=True, null=True) # ID de escuela principal
    fechaConformacion = models.DateField(default=None, blank=True, null=True)
    motivoDeConformacion = models.ForeignKey('MotivoDeConformacion', related_name='escuelas', default=None, blank=True, null=True)
    conformada = models.BooleanField(default=False)

    estado = models.BooleanField(default=True, blank=True) # True = Abierta, False= Cerrada

    def __unicode__(self):
        return self.cue + " " + self.nombre

    class Meta:
        db_table = 'escuelas'
        verbose_name_plural = "escuelas"

    class JSONAPIMeta:
        resource_name = 'escuelas'

    def conformar_con(self, escuela_que_se_absorbera, motivo):
        assert not escuela_que_se_absorbera.padre        # No permite re-absorber
        assert not escuela_que_se_absorbera == self      # Ni conformarse consigo misma
        assert not self.padre                           # Ni conformar una escuela ya conformada por otra

        escuela_que_se_absorbera.padre = self
        escuela_que_se_absorbera.motivoDeConformacion = motivo
        escuela_que_se_absorbera.fechaConformacion = datetime.date.today()
        escuela_que_se_absorbera.conformada = True

        escuela_que_se_absorbera.save()
