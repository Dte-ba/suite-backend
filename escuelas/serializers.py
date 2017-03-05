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
        fields = ('id', 'numero', 'municipios')

class PerfilSerializer(CustomSerializer):

    class Meta:
        model = models.Perfil
        fields = '__all__'

class MunicipioSerializer(CustomSerializer):

    class Meta:
        model = models.Municipio
        fields = '__all__'
