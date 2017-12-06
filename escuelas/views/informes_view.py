from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

class InformesViewSet(viewsets.ViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        if not request.user.is_authenticated():
            return Response({'error': 'El usuario no esta autenticado.'})

        perfil_id = self.request.query_params.get('perfil_id', None)
        desde = self.request.query_params.get('desde', None)
        hasta = self.request.query_params.get('hasta', None)

        if None in [perfil_id, desde, hasta]:
            return Response({
                'error': "No han especificado todos los argumentos: perfil_id, desde y hasta."
            })

        data = {
            'eventos': []
        }

        return Response(data)
