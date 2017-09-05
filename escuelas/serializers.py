from django.contrib.auth.models import User
from rest_framework import serializers
import models
from rest_framework_json_api.relations import ResourceRelatedField
from django.contrib.auth.models import Permission, Group
import json

class CustomSerializer(serializers.HyperlinkedModelSerializer):

    def get_field_names(self, declared_fields, info):
        expanded_fields = super(CustomSerializer, self).get_field_names(declared_fields, info)

        if getattr(self.Meta, 'extra_fields', None):
            return expanded_fields + self.Meta.extra_fields

        return expanded_fields

class UserSerializer(CustomSerializer):

    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff')

class ContactoSerializer(CustomSerializer):

    class Meta:
        model = models.Contacto
        fields = '__all__'

class EventoSerializer(CustomSerializer):

    responsable = ResourceRelatedField(queryset=models.Perfil.objects)
    escuela = ResourceRelatedField(queryset=models.Escuela.objects)
    categoria = ResourceRelatedField(queryset=models.CategoriaDeEvento.objects)
    acompaniantes = ResourceRelatedField(queryset=models.Perfil.objects, many=True)

    class Meta:
        model = models.Evento
        fields = ('id', 'titulo', 'fecha', 'fecha_fin', 'inicio', 'fin', 'todoElDia', 'objetivo', 'responsable', 'escuela', 'acompaniantes', 'cantidadDeParticipantes', 'requiereTraslado', 'categoria', 'resumenParaCalendario', 'minuta', 'acta_legacy', 'legacy_id')


class RegionSerializer(CustomSerializer):

    class Meta:
        model = models.Region
        fields = "__all__"


class CargoSerializer(CustomSerializer):

    class Meta:
        model = models.Cargo
        fields = '__all__'

class PerfilSerializer(CustomSerializer):

    cargo = CargoSerializer()

    class Meta:
        model = models.Perfil
        fields = ('user', 'group', 'image', 'nombre', 'apellido', 'fechadenacimiento', 'titulo', 'experiencia', 'dni', 'cuit', 'cbu', 'email', 'estado', 'direccionCalle', 'direccionAltura', 'direccionPiso', 'direccionDepto', 'direccionTorre', 'codigoPostal', 'localidad', 'telefonoCelular', 'telefonoAlternativo', 'region', 'cargo', 'contrato', 'expediente', 'fechaDeIngreso', 'fechaDeRenuncia', 'emailLaboral')
        read_only_fields = ('image',)

class DistritoSerializer(CustomSerializer):

    region = RegionSerializer()

    class Meta:
        model = models.Distrito
        fields = "__all__"

class LocalidadSerializer(CustomSerializer):

    distrito = DistritoSerializer()

    class Meta:
        model = models.Localidad
        fields = "__all__"

class ProgramaSerializer(CustomSerializer):

    #escuelas = EscuelaSerializer(many=True, read_only=True)

    class Meta:
        model = models.Programa
        fields = "__all__"
        extra_fields = ['cantidadDeEscuelas']

class TipoDeFinanciamientoSerializer(CustomSerializer):

    class Meta:
        model = models.TipoDeFinanciamiento
        fields = "__all__"

class TipoDeGestionSerializer(CustomSerializer):

    class Meta:
        model = models.TipoDeGestion
        fields = "__all__"

class AreaSerializer(CustomSerializer):

    class Meta:
        model = models.Area
        fields = "__all__"

class NivelSerializer(CustomSerializer):

    class Meta:
        model = models.Nivel
        fields = "__all__"

class ModalidadSerializer(CustomSerializer):

    class Meta:
        model = models.Modalidad
        fields = "__all__"

class PisoSerializer(CustomSerializer):

    class Meta:
        model = models.Piso
        fields = "__all__"

class MotivoDeConformacionSerializer(CustomSerializer):

    class Meta:
        model = models.MotivoDeConformacion
        fields = "__all__"



class SubEscuelaSerializer(CustomSerializer):

    class Meta:
        model = models.Escuela
        fields = ('cue', 'nombre',)

class EscuelaSerializer(CustomSerializer):

    localidad = LocalidadSerializer()
    tipo_de_financiamiento = ResourceRelatedField(queryset=models.TipoDeFinanciamiento.objects)
    nivel = NivelSerializer()
    modalidad = ModalidadSerializer()
    tipo_de_gestion = ResourceRelatedField(queryset=models.TipoDeGestion.objects)
    area = AreaSerializer()
    programas = ProgramaSerializer(many=True, read_only=True)
    piso = ResourceRelatedField(queryset=models.Piso.objects)
    contactos = ContactoSerializer(many=True, read_only=True)
    subescuelas = SubEscuelaSerializer(many=True, read_only=True)
    padre = ResourceRelatedField(queryset=models.Escuela.objects)
    motivo_de_conformacion = ResourceRelatedField(queryset=models.MotivoDeConformacion.objects)

    class Meta:
        model = models.Escuela
        fields = ('cue', 'nombre', 'direccion', 'telefono', 'email', 'latitud', 'longitud', 'localidad', 'tipo_de_financiamiento', 'nivel', 'modalidad', 'tipo_de_gestion', 'area', 'programas', 'piso', 'contactos', 'padre', 'fecha_conformacion', 'motivo_de_conformacion', 'estado', 'conformada', 'padre', 'subescuelas')


class ExperienciaSerializer(CustomSerializer):

    class Meta:
        model = models.Experiencia
        fields = '__all__'


class ContratoSerializer(CustomSerializer):

    class Meta:
        model = models.Contrato
        fields = '__all__'

class CargoEscolarSerializer(CustomSerializer):

    class Meta:
        model = models.CargoEscolar
        fields = '__all__'

class ComentarioDeTareaSerializer(CustomSerializer):

    class Meta:
        model = models.ComentarioDeTarea
        fields = '__all__'

class MotivoDeTareaSerializer(CustomSerializer):

    class Meta:
        model = models.MotivoDeTarea
        fields = '__all__'

class EstadoDeTareaSerializer(CustomSerializer):

    class Meta:
        model = models.EstadoDeTarea
        fields = '__all__'

class PrioridadDeTareaSerializer(CustomSerializer):

    class Meta:
        model = models.PrioridadDeTarea
        fields = '__all__'

class TareaSerializer(CustomSerializer):
    autor = ResourceRelatedField(queryset=models.Perfil.objects)
    responsable = ResourceRelatedField(queryset=models.Perfil.objects)
    motivo_de_tarea = ResourceRelatedField(queryset=models.MotivoDeTarea.objects)
    estado_de_tarea = ResourceRelatedField(queryset=models.EstadoDeTarea.objects)
    prioridad_de_tarea = ResourceRelatedField(queryset=models.PrioridadDeTarea.objects)
    escuela = ResourceRelatedField(queryset=models.Escuela.objects)
    # comentarios_tarea = ComentarioDeTareaSerializer(many=True, read_only=True)
    # comentarios_de_tarea = ResourceRelatedField(queryset=models.ComentarioDeTarea.objects, many=True)

    class Meta:
        model = models.Tarea
        fields = ('titulo', 'fecha_de_alta', 'autor', 'responsable', 'descripcion', 'motivo_de_tarea', 'estado_de_tarea', 'prioridad_de_tarea', 'escuela')

class CategoriaDeEventoSerializer(CustomSerializer):

    class Meta:
        model = models.CategoriaDeEvento
        fields = '__all__'

class EstadoDeValidacionSerializer(CustomSerializer):

    class Meta:
        model = models.EstadoDeValidacion
        fields = '__all__'


class ComentarioDeValidacionSerializer(CustomSerializer):

    autor = ResourceRelatedField(queryset=models.Perfil.objects)

    class Meta:
        model = models.ComentarioDeValidacion
        fields = '__all__'

class ValidacionSerializer(CustomSerializer):
    autor = ResourceRelatedField(queryset=models.Perfil.objects)
    escuela = ResourceRelatedField(queryset=models.Escuela.objects)
    estado = ResourceRelatedField(queryset=models.EstadoDeValidacion.objects)
    comentariosDeValidacion = ResourceRelatedField(queryset=models.ComentarioDeValidacion.objects, many=True)

    class Meta:
        model = models.Validacion
        fields = ('autor', 'fechaDeAlta', 'escuela', 'estado', 'comentariosDeValidacion')


class EstadoDePaqueteSerializer(CustomSerializer):

    class Meta:
        model = models.EstadoDePaquete
        fields = '__all__'

class PaqueteSerializer(CustomSerializer):

    escuela = ResourceRelatedField(queryset=models.Escuela.objects)
    estado = ResourceRelatedField(queryset=models.EstadoDePaquete.objects)

    class Meta:
        model = models.Paquete
        fields = (
            'escuela',
            'fechaPedido',
            'ne',
            'idHardware',
            'marcaDeArranque',
            'comentario',
            'carpetaPaquete',
            'fechaEnvio',
            'zipPaquete',
            'estado',
            'fechaDevolucion',
            'leido'
        )

class PermissionSerializer(CustomSerializer):
    content_type = serializers.CharField(source='content_type.model', read_only=True)

    class Meta:
        model = Permission
        fields = ('name', 'codename', 'content_type')

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    perfiles = ResourceRelatedField(read_only=True, many=True)
    permissions = ResourceRelatedField(read_only=True, many=True)

    class Meta:
        model = Group
        fields = ('url', 'name', 'perfiles', 'permissions')
