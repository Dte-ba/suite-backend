from django.contrib.auth.models import User
from rest_framework import serializers
import models

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

class EscuelaSerializer(CustomSerializer):

    class Meta:
        model = models.Escuela
        fields = '__all__'
        extra_fields = ['contactos']

class ContactoSerializer(CustomSerializer):

    class Meta:
        model = models.Contacto
        fields = '__all__'

class EventoSerializer(CustomSerializer):

    class Meta:
        model = models.Evento
        fields = '__all__'

class RegionSerializer(CustomSerializer):

    class Meta:
        model = models.Region
        fields = ('id', 'numero')

class PerfilSerializer(CustomSerializer):

    class Meta:
        model = models.Perfil
        fields = '__all__'
        read_only_fields = ('image',)

class DistritoSerializer(CustomSerializer):

    class Meta:
        model = models.Distrito
        fields = '__all__'

class LocalidadSerializer(CustomSerializer):

    class Meta:
        model = models.Localidad
        fields = '__all__'

class ProgramaSerializer(CustomSerializer):

    class Meta:
        model = models.Programa
        fields = '__all__'

class TipoDeFinanciamientoSerializer(CustomSerializer):

    class Meta:
        model = models.TipoDeFinanciamiento
        fields = '__all__'

class TipoDeGestionSerializer(CustomSerializer):

    class Meta:
        model = models.TipoDeGestion
        fields = '__all__'

class AreaSerializer(CustomSerializer):

    class Meta:
        model = models.Area
        fields = '__all__'

class NivelSerializer(CustomSerializer):

    class Meta:
        model = models.Nivel
        fields = '__all__'
