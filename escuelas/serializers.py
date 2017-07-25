from django.contrib.auth.models import User
from rest_framework import serializers
import models
from rest_framework_json_api.relations import ResourceRelatedField

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

    class Meta:
        model = models.Evento
        fields = '__all__'

class RegionSerializer(CustomSerializer):

    class Meta:
        model = models.Region
        fields = "__all__"

class PerfilSerializer(CustomSerializer):

    class Meta:
        model = models.Perfil
        fields = '__all__'
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

    class Meta:
        model = models.Programa
        fields = "__all__"

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

class PisoSerializer(CustomSerializer):

    class Meta:
        model = models.Piso
        fields = "__all__"

class EscuelaSerializer(CustomSerializer):

    # included_serializers = {
    #     'localidad': LocalidadSerializer,
    # }
    localidad = LocalidadSerializer()
    tipoDeFinanciamiento = TipoDeFinanciamientoSerializer()
    nivel = NivelSerializer()
    tipoDeGestion = TipoDeGestionSerializer()
    area = AreaSerializer()
    programas = ProgramaSerializer(many=True, read_only=True)
    piso = PisoSerializer()
    contactos = ContactoSerializer(many=True, read_only=True)

    class Meta:
        model = models.Escuela
        fields = ('cue', 'nombre', 'direccion', 'telefono', 'email', 'latitud', 'longitud', 'localidad', 'tipoDeFinanciamiento', 'nivel', 'tipoDeGestion', 'area', 'programas', 'piso', 'contactos')

    # class JSONAPIMeta:
    #     included_resources = ['localidad']

class ExperienciaSerializer(CustomSerializer):

    class Meta:
        model = models.Experiencia
        fields = '__all__'

class CargoSerializer(CustomSerializer):

    class Meta:
        model = models.Cargo
        fields = '__all__'

class ContratoSerializer(CustomSerializer):

    class Meta:
        model = models.Contrato
        fields = '__all__'

class CargoEscolarSerializer(CustomSerializer):

    class Meta:
        model = models.CargoEscolar
        fields = '__all__'

class ComentarioTareaSerializer(CustomSerializer):

    class Meta:
        model = models.ComentarioTarea
        fields = '__all__'

class MotivoTareaSerializer(CustomSerializer):

    class Meta:
        model = models.MotivoTarea
        fields = '__all__'

class EstadoTareaSerializer(CustomSerializer):

    class Meta:
        model = models.EstadoTarea
        fields = '__all__'

class PrioridadTareaSerializer(CustomSerializer):

    class Meta:
        model = models.PrioridadTarea
        fields = '__all__'

class TareaSerializer(CustomSerializer):
    autor = ResourceRelatedField(queryset=models.Perfil.objects)
    responsable = ResourceRelatedField(queryset=models.Perfil.objects)
    motivo = ResourceRelatedField(queryset=models.MotivoTarea.objects)
    estado = ResourceRelatedField(queryset=models.EstadoTarea.objects)
    prioridad = ResourceRelatedField(queryset=models.PrioridadTarea.objects)
    escuela = ResourceRelatedField(queryset=models.Escuela.objects)

    class Meta:
        model = models.Tarea
        fields = ('titulo', 'fechaDeAlta', 'autor', 'responsable', 'descripcion', 'motivo', 'estado', 'prioridad', 'escuela')
