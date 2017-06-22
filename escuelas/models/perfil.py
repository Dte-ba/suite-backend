# coding: utf-8
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

def upload_to(instance, filename):
    return 'user_profile_image/{}/{}'.format(instance.user_id, filename)

class Perfil(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, default=1)

    # 1) Datos Personales
    image = models.ImageField('image', blank=True, null=True, upload_to=upload_to)
    nombre = models.CharField(max_length=200, default="")
    apellido = models.CharField(max_length=200, default="")
    fechadenacimiento = models.DateField(default="2010-10-10")
    titulo = models.CharField(max_length=200, default=None, blank=True, null=True)
    # Perfil / Experiencia - definir
    dni = models.CharField(max_length=200, default="0000")
    cuit = models.CharField(max_length=200, default="0000")
    cbu = models.CharField(max_length=50, default=None, blank=True, null=True)
    email = models.CharField(max_length=200, default=None, blank=True, null=True)

    # Dirección Particular
    direccionCalle = models.CharField(max_length=200, default=None, blank=True, null=True)
    direccionAltura = models.CharField(max_length=20, default=None, blank=True, null=True)
    direccionPiso = models.CharField(max_length=3, default=None, blank=True, null=True)
    direccionDepto = models.CharField(max_length=3, default=None, blank=True, null=True)
    direccionTorre = models.CharField(max_length=200, default=None, blank=True, null=True)
    codigoPostal = models.CharField(max_length=15, default=None, blank=True, null=True)
    # Ver si partido es lo mismo que distrito
    localidad = models.ForeignKey('Localidad', related_name='perfiles', default=None, blank=True, null=True) # Evaluar si la lista de localidades es la mejor opción.
    telefonoCelular = models.CharField(max_length=25, default=None, blank=True, null=True)
    telefonoAlternativo = models.CharField(max_length=25, default=None, blank=True, null=True)

    # 2) Datos administrativos
    # permisosSuite =
    region = models.ForeignKey('region', related_name='perfiles', default=None, blank=True, null=True)
    cargo = models.CharField(max_length=200, default=None, blank=True, null=True) # Evaluar hacer un select en base a modelo
    Contrato = models.CharField(max_length=200, default=None, blank=True, null=True) # Evaluar hacer un select en base a modelo. Este campo es Programa/Contrato, no sería el mismo model que el programa de escuelas
    expediente = models.CharField(max_length=25, default=None, blank=True, null=True)
    fechaDeIngreso = models.DateField(default="2010-10-10")
    fechaDeReuncia = models.DateField(default=None, blank=True,null=True)
    emailLaboral = models.CharField(max_length=200, default=None, blank=True, null=True)

    # 3) Disponibilidad Horaria (?):

    # 4) Adjuntos:
    # curriculum =
    # constanciaArba =
    # constanciaMonotributo =
    # constanciaCBU =
    # contrato =

    # 5) Dispositivos asignados:
    # Depende de que esté creado el módulo de stock.

    def __unicode__(self):
        return self.dni

    class Meta:
        db_table = 'perfiles'
        verbose_name_plural = "perfiles"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.perfil.save()
