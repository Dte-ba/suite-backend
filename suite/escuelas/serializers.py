from django.contrib.auth.models import User
from rest_framework import serializers
import models

class UserSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff')

class EscuelaSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.Escuela
        fields = '__all__'
