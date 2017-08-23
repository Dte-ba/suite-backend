# coding: utf-8
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_save
from django.dispatch import receiver

def upload_to(instance, filename):
    return 'user_profile_image/{}/{}'.format(instance.user_id, filename)

class Perfil(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, related_name="perfiles", default=None, null=True)

    # 1) Datos Personales
    image = models.ImageField('image', blank=True, null=True, upload_to=upload_to)
    nombre = models.CharField(max_length=200, default="")
    apellido = models.CharField(max_length=200, default="")
    fechadenacimiento = models.DateField(default=None, blank=True,null=True)
    titulo = models.CharField(max_length=200, default=None, blank=True, null=True)
    experiencia = models.ForeignKey('Experiencia', related_name='perfiles', default=None, blank=True, null=True)
    dni = models.CharField(max_length=200, default="0000")
    cuit = models.CharField(max_length=200, default="0000")
    cbu = models.CharField(max_length=50, default=None, blank=True, null=True)
    email = models.CharField(max_length=200, default=None, blank=True, null=True)
    estado = models.BooleanField(default=1)

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
    cargo = models.ForeignKey('cargo', related_name='perfiles', default=None, blank=True, null=True)
    contrato = models.ForeignKey('contrato', related_name='perfiles', default=None, blank=True, null=True)
    expediente = models.CharField(max_length=25, default=None, blank=True, null=True)
    fechaDeIngreso = models.DateField(default="2010-10-10")
    fechaDeRenuncia = models.DateField(default=None, blank=True,null=True)
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
        return u"Perfil: " + self.apellido + ", " + self.nombre + " - DNI: " + self.dni

    class Meta:
        db_table = 'perfiles'
        verbose_name_plural = "perfiles"

    class JSONAPIMeta:
        resource_name = 'perfiles'

    def obtenerListaDeGrupos(self):
        if self.group:
            return [{'id': self.group.id, 'nombre': self.group.name}]
        else:
            return []

    def obtenerPermisos(self):
        todos_los_permisos = Permission.objects.all()

        if self.group:
            permisos_del_grupo = self.group.permissions.all()
        else:
            permisos_del_grupo = []

        permisos_que_no_tiene = set(todos_los_permisos) - set(permisos_del_grupo)

        permisos_como_diccionario = {p.codename: (p in permisos_del_grupo)
                                                for p in todos_los_permisos}

        return permisos_como_diccionario

    def definir_grupo_usando_nombre(self, nombre_del_grupo):
        self.group = Group.objects.get(name=nombre_del_grupo)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(user=instance)
