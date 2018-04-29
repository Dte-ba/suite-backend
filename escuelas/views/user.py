# coding: utf-8
from __future__ import unicode_literals
from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from escuelas import serializers


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @list_route(methods=['post'])
    def create_user(self, request):
        permission_classes = (AllowAny,)
        serialized = serializers.UserSerializer(data=request.data, context={'request': request})

        if serialized.is_valid():
            usuario = serialized.save()

            resultado = {
                "idPerfil": usuario.perfil.id,
                "idUsuario": usuario.id,
                "data": serialized.data
            }

            return Response(resultado, status=status.HTTP_201_CREATED)
        else:
            values = serialized._errors
            values['errors'] = [{"detail": i[1], "source": {'pointer': i[0]}} for i in values.items()]
            return Response(values, status=status.HTTP_400_BAD_REQUEST)