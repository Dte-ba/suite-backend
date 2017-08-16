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
    # acompaniantes = ResourceRelatedField(queryset=models.Perfil.objects)
    acompaniantes = ResourceRelatedField(queryset=models.Perfil.objects, many=True)

    class Meta:
        model = models.Evento
        fields = ('titulo', 'fecha', 'fecha_fin', 'inicio', 'fin', 'todoElDia', 'objetivo', 'responsable', 'escuela', 'acompaniantes', 'cantidadDeParticipantes', 'requiereTraslado')

class RegionSerializer(CustomSerializer):

    class Meta:
        model = models.Region
        fields = "__all__"

class PerfilSerializer(CustomSerializer):

    eventos_acompaniantes = EventoSerializer(many=True, read_only=True)

    class Meta:
        model = models.Perfil
        fields = ('user', 'grupo', 'image', 'nombre', 'apellido', 'fechadenacimieto', 'titulo', 'experiencia', 'dni', 'cuit', 'cbu', 'email', 'estado', 'direccionCalle', 'direccionAltura', 'direccionPiso', 'direccionDepto', 'direccionTorre', 'codigoPostal', 'localidad', 'telefonoCelular', 'telefonoAlternativo', 'region', 'cargo', 'contrato', 'expediente', 'fechaDeIngreso', 'fechaDeRenuncia', 'emailLaboral', 'eventos_acompaniantes')
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

class PisoSerializer(CustomSerializer):

    class Meta:
        model = models.Piso
        fields = "__all__"

class MotivoDeConformacionSerializer(CustomSerializer):

    class Meta:
        model = models.MotivoDeConformacion
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
    padre = ResourceRelatedField(queryset=models.Escuela.objects)
    motivoDeConformacion = ResourceRelatedField(queryset=models.MotivoDeConformacion.objects)

    class Meta:
        model = models.Escuela
        fields = ('cue', 'nombre', 'direccion', 'telefono', 'email', 'latitud', 'longitud', 'localidad', 'tipoDeFinanciamiento', 'nivel', 'tipoDeGestion', 'area', 'programas', 'piso', 'contactos', 'padre', 'fechaConformacion', 'motivoDeConformacion', 'estado')

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
    motivoDeTarea = ResourceRelatedField(queryset=models.MotivoDeTarea.objects)
    estadoDeTarea = ResourceRelatedField(queryset=models.EstadoDeTarea.objects)
    prioridadDeTarea = ResourceRelatedField(queryset=models.PrioridadDeTarea.objects)
    escuela = ResourceRelatedField(queryset=models.Escuela.objects)
    # comentarios_tarea = ComentarioDeTareaSerializer(many=True, read_only=True)
    comentariosDeTarea = ResourceRelatedField(queryset=models.ComentarioDeTarea.objects, many=True)

    class Meta:
        model = models.Tarea
        fields = ('titulo', 'fechaDeAlta', 'autor', 'responsable', 'descripcion', 'motivoDeTarea', 'estadoDeTarea', 'prioridadDeTarea', 'escuela', 'comentariosDeTarea')

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
