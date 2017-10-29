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
    tipo_de_financiamiento = models.ManyToManyField('TipoDeFinanciamiento', related_name='escuelas', default=None, blank=True, null=True)
    nivel = models.ForeignKey('Nivel', related_name='escuelas', default=None, blank=True, null=True)
    tipo_de_gestion = models.ForeignKey('TipoDeGestion', related_name='escuelas', default=None, blank=True, null=True)
    area = models.ForeignKey('Area', related_name='escuelas', default=None, blank=True, null=True)
    programas = models.ManyToManyField('Programa', related_name='escuelas')
    piso = models.OneToOneField('Piso', related_name='escuela', default=None, blank=True, null=True)
    modalidad = models.ForeignKey('Modalidad', related_name='escuelas', default=None, blank=True, null=True)



    # Para conformaciones
    padre = models.ForeignKey('self', related_name='subescuelas', on_delete=models.CASCADE, default=None, blank=True, null=True) # ID de escuela principal
    fecha_conformacion = models.DateField(default=None, blank=True, null=True)
    motivo_de_conformacion = models.ForeignKey('MotivoDeConformacion', related_name='escuelas', default=None, blank=True, null=True)
    conformada = models.BooleanField(default=False)

    estado = models.BooleanField(default=True, blank=True) # True = Abierta, False= Cerrada

    def __unicode__(self):
        return self.cue + " " + self.nombre

    class Meta:
        db_table = 'escuelas'
        verbose_name_plural = "escuelas"

    class JSONAPIMeta:
        resource_name = 'escuelas'

    def conformar_con(self, escuela_que_se_absorbera, motivo, fecha=None):

        if escuela_que_se_absorbera.padre:
            raise Exception('La escuela seleccionada (cue: %s) ya fue conformada' %(escuela_que_se_absorbera.cue))

        if escuela_que_se_absorbera == self:
            raise Exception('No se puede conformar una escuela consigo misma')

        escuela_que_se_absorbera.padre = self
        escuela_que_se_absorbera.motivo_de_conformacion = motivo

        if fecha:
            escuela_que_se_absorbera.fecha_conformacion = fecha
        else:
            escuela_que_se_absorbera.fecha_conformacion = datetime.date.today()

        escuela_que_se_absorbera.conformada = True

        escuela_que_se_absorbera.save()

    def numero_de_region(self):
        try:
            return self.localidad.distrito.region.numero
        except:
            return ""
