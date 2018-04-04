# coding: utf-8
import os
from django_rq import get_worker

from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.files import File
from rest_framework.test import APITestCase
from django.core.files.base import ContentFile

from escuelas import models
from escuelas import serializers
from escuelas import fixture
from escuelas import trabajos

get_worker().work(burst=True)

class TrabajosPaquetes(APITestCase):

    def test_puede_crear_paquete_de_provision(self):
        # Prepara el usuario para chequear contra la api
        user = User.objects.create_user(username='test', password='123')
        self.client.force_authenticate(user=user)

        # Se genera un grupo
        grupo = Group.objects.create(name="Administrador")

        # Se genera un usuario demo
        user_2 = User.objects.create_user(username='demo', password='123')
        user_2.perfil.group = grupo
        user_2.perfil.save()

        # Se genera 1 escuela
        region_1 = models.Region.objects.create(numero=1)
        distrito_1 = models.Distrito.objects.create(nombre="distrito1", region=region_1)
        localidad_1 = models.Localidad.objects.create(nombre="localidad1", distrito=distrito_1)
        escuela_1 = models.Escuela.objects.create(cue="1", nombre="Escuela 1", localidad=localidad_1)

        # Se crea un estado de paquete
        estado = models.EstadoDePaquete.objects.create(nombre="Pendiente")

        # Se crea un pedido de paquete
        paquete_1 = models.Paquete.objects.create(
            escuela=escuela_1,
            fecha_pedido="2017-11-09",
            ne="ee183ce07cfbd86bf819",
            id_hardware="E81132429EFF",
            marca_de_arranque="23",        # Corresponde a 17 hexa
            estado=estado
        )

        # Se pide la lista de paquetes
        response = self.client.get('/api/paquetes', format='json')

        # Tiene que existir un paquete
        self.assertEqual(models.Paquete.objects.all().count(), 1)

    def test_puede_exportar_paquetes_con_llaves(self):
        (escuela_1, escuela_2) = self._crear_escuelas_con_llaves()

        self._crear_paquetes_pendientes(escuela_1, escuela_2)

        # Se pide la lista de paquetes, tienen que haber 3 paquetes.
        self.assertEqual(models.Paquete.objects.all().count(), 3)

        # Se pide la lista de paquetes, tienen que haber 3 paquetes.
        response = self.client.get('/api/paquetes/export_raw?inicio=2017-01-01&fin=2018-03-30&estado=Pendiente', format='json')
        self.assertEqual(len(response.data['tabla']), 3)
        self.assertEqual(len(response.data['llaves']), 2)

    def test_puede_distribuir_paquetes_con_devolucion_de_educar(self):
        (escuela_1, escuela_2) = self._crear_escuelas_con_llaves()
        self._crear_paquetes_para_probar_distribucion(escuela_1, escuela_2)

        usuario = User.objects.create_user(username='demo', password='123')
        usuario.perfil.save()

        archivo_django = self._obtener_archivo_para_distribuir_paquetes()

        distribucion = models.DistribucionDePaquete.objects.create()

        distribucion.archivo.save("PBA1218Varios.zip", archivo_django)

        estado_educar = models.EstadoDePaquete.objects.get(nombre="EducAr")
        paquetes_con_estado_educar = models.Paquete.objects.filter(estado=estado_educar).count()
        self.assertEqual(paquetes_con_estado_educar, 4)

        trabajos.distribuir_paquetes.distribuir_paquetes(distribucion)

        pendientes_luego_de_distribuir = models.Paquete.objects.filter(estado=estado_educar).count()
        self.assertEqual(pendientes_luego_de_distribuir, 3)

        estado_recibido = models.EstadoDePaquete.objects.get(nombre="Devuelto")
        recibidos = models.Paquete.objects.filter(estado=estado_recibido).count()
        self.assertEqual(recibidos, 1)

    def _obtener_archivo_para_distribuir_paquetes(self):
        base = os.path.dirname(__file__)
        path = os.path.join(base, "fixtures/distribucion_de_paquetes__PBA1218Varios.zip")

        archivo = open(path)
        archivo_django = ContentFile(archivo.read());
        archivo.close()
        return archivo_django

    def _crear_paquetes_para_probar_distribucion(self, escuela_1, escuela_2):
        estado_pendiente = models.EstadoDePaquete.objects.create(nombre="Pendiente")
        estado_educar = models.EstadoDePaquete.objects.create(nombre="EducAr")
        estado_devuelto = models.EstadoDePaquete.objects.create(nombre="Devuelto")

        paquete_1 = models.Paquete.objects.create(
            escuela=escuela_1,
            fecha_pedido="2017-11-09",
            ne="ee183ce07cfbd86bf001",
            id_hardware="240a64647f81",
            marca_de_arranque="6",
            estado=estado_educar,
            ma_hexa="39bf408"
        )

        paquete_2 = models.Paquete.objects.create(
            escuela=escuela_2,
            fecha_pedido="2017-11-10",
            ne="ee183ce07cfbd86bf819",
            id_hardware="E81132429EFF",
            marca_de_arranque="23",        # Corresponde a 17 hexa
            estado=estado_educar,
            ma_hexa="17"
        )

        paquete_3 = models.Paquete.objects.create(
            escuela=escuela_2,
            fecha_pedido="2017-11-11",
            ne="ee183ce07cfbd86bf003",
            id_hardware="240a64647f83",
            marca_de_arranque="6",
            estado=estado_educar,
            ma_hexa="39cbd34"
        )

        paquete_4 = models.Paquete.objects.create(
            escuela=escuela_2,
            fecha_pedido="2017-11-11",
            ne="ee183ce07cfbd86bf003",
            id_hardware="240a64647f83",
            marca_de_arranque="6",
            estado=estado_educar,
            ma_hexa="FFFFFFFFFF"
        )

    def _crear_paquetes_pendientes(self, escuela_1, escuela_2):
        estado_pendiente = models.EstadoDePaquete.objects.create(nombre="Pendiente")
        estado_educar = models.EstadoDePaquete.objects.create(nombre="EducAr")

        paquete_1 = models.Paquete.objects.create(
            escuela=escuela_1,
            fecha_pedido="2017-11-09",
            ne="ee183ce07cfbd86bf001",
            id_hardware="240a64647f81",
            marca_de_arranque="6",
            estado=estado_pendiente
        )

        paquete_2 = models.Paquete.objects.create(
            escuela=escuela_2,
            fecha_pedido="2017-11-10",
            ne="ee183ce07cfbd86bf002",
            id_hardware="240a64647f82",
            marca_de_arranque="6",
            estado=estado_pendiente
        )

        paquete_3 = models.Paquete.objects.create(
            escuela=escuela_2,
            fecha_pedido="2017-11-11",
            ne="ee183ce07cfbd86bf003",
            id_hardware="240a64647f83",
            marca_de_arranque="6",
            estado=estado_pendiente
        )

    def _crear_escuelas_con_llaves(self):
        region_1 = models.Region.objects.create(numero=1)
        distrito_1 = models.Distrito.objects.create(nombre="distrito1", region=region_1)
        localidad_1 = models.Localidad.objects.create(nombre="localidad1", distrito=distrito_1)

        piso_1 = models.Piso.objects.create(servidor="Servidor EXO")
        piso_2 = models.Piso.objects.create(servidor="Servidor EXO de la escuela 2")

        self.vincular_llave(piso_1, 'fixtures/llave_3tcQe4d.zip')
        self.vincular_llave(piso_2, 'fixtures/llave_qi1hxrc.zip')

        escuela_1 = models.Escuela.objects.create(
            cue="1",
            nombre="Escuela 1",
            localidad=localidad_1,
            piso=piso_1)

        escuela_2 = models.Escuela.objects.create(
            cue="2",
            nombre="Escuela 2",
            localidad=localidad_1,
            piso=piso_2)

        return (escuela_1, escuela_2)

    def vincular_llave(self, piso, ruta):
        base = os.path.dirname(__file__)
        local_file = open(os.path.join(base, ruta))
        djangofile = File(local_file)
        piso.llave.save(ruta, djangofile)
        local_file.close()
        piso.save()

    def test_puede_exportar_paquetes_como_trabajo_no_asincronico(self):
        (escuela_1, escuela_2) = self._crear_escuelas_con_llaves()
        self._crear_paquetes_pendientes(escuela_1, escuela_2)

        user = User.objects.create_user(username='test', password='123')
        self.client.force_authenticate(user=user)

        resultado = trabajos.paquetes.exportar_paquetes(inicio="2017-01-01", fin="2018-03-30", estadoPedido="Pendiente")
        self.assertTrue(resultado.archivo)

    def test_puede_exportar_paquetes_como_trabajo(self):
        (escuela_1, escuela_2) = self._crear_escuelas_con_llaves()
        self._crear_paquetes_pendientes(escuela_1, escuela_2)

        user = User.objects.create_user(username='test', password='123')
        self.client.force_authenticate(user=user)

        response = self.client.get('/api/trabajos/exportar_paquetes?inicio=2017-01-01&fin=2018-03-30&estado=Pendiente')
        self.assertTrue(response.data['trabajo_id'])
