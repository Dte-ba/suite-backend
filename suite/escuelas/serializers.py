from django.contrib.auth.models import User
from rest_framework import serializers
import models

class CustomSerializer(serializers.HyperlinkedModelSerializer):

    def get_field_names(self, declared_fields, info):
        parent_class = super(CustomSerializer, self)
        expanded_fields = perent_class.get_field_names(declared_fields, info)

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
