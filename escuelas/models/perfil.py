# coding: utf-8
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_save
from django.db.models import Q
from django.dispatch import receiver
from escuelas import utils
from escuelas.models import Evento


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
    direccion_calle = models.CharField(max_length=200, default=None, blank=True, null=True)
    direccion_altura = models.CharField(max_length=20, default=None, blank=True, null=True)
    direccion_piso = models.CharField(max_length=3, default=None, blank=True, null=True)
    direccion_depto = models.CharField(max_length=3, default=None, blank=True, null=True)
    direccion_torre = models.CharField(max_length=200, default=None, blank=True, null=True)
    codigo_postal = models.CharField(max_length=15, default=None, blank=True, null=True)
    # Ver si partido es lo mismo que distrito
    localidad = models.ForeignKey('Localidad', related_name='perfiles', default=None, blank=True, null=True) # Evaluar si la lista de localidades es la mejor opción.
    telefono_celular = models.CharField(max_length=25, default=None, blank=True, null=True)
    telefono_alternativo = models.CharField(max_length=25, default=None, blank=True, null=True)

    # 2) Datos administrativos
    # permisosSuite =
    region = models.ForeignKey('region', related_name='perfiles', default=None, blank=True, null=True)
    cargo = models.ForeignKey('cargo', related_name='perfiles', default=None, blank=True, null=True)
    contrato = models.ForeignKey('contrato', related_name='perfiles', default=None, blank=True, null=True)
    expediente = models.CharField(max_length=25, default=None, blank=True, null=True)
    fecha_de_ingreso = models.DateField(default="2010-10-10")
    fecha_de_renuncia = models.DateField(default=None, blank=True,null=True)
    email_laboral = models.CharField(max_length=200, default=None, blank=True, null=True)

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
        return u"Perfil: ("+ str(self.id) +") " + self.apellido + ", " + self.nombre + " - DNI: " + self.dni

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

    def esAdministrador(self):
        permisos = self.obtenerPermisos()
        return 'perfil.global' in permisos and permisos['perfil.global']

    def definir_grupo_usando_nombre(self, nombre_del_grupo):
        self.group = Group.objects.get(name=nombre_del_grupo)

    def enviar_correo(self, asunto, mensaje):
        utils.enviar_correo(desde="hugoruscitti@gmail.com", hasta="hugoruscitti@gmail.com", asunto=asunto, mensaje=mensaje)

    def obtener_eventos_por_fecha(self, desde, hasta):
        filtro = Q(responsable=self) | Q(acompaniantes=self)
        return Evento.objects.filter(filtro).filter(fecha__range=(desde, hasta)).distinct().order_by('fecha')


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(user=instance)
