# coding: utf-8
from __future__ import unicode_literals
from rest_framework.test import APITestCase


class Scripts(APITestCase):

    def test_puede_buscar_localidades_y_distritos_duplicados(self):
        from scripts import limpiar_registros_duplicados
        limpiar_registros_duplicados.eliminar_duplicados(solo_simular=True, verbose=False)