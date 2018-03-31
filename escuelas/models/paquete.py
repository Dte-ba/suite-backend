# coding: utf-8
import datetime
from escuelas.models import EstadoDePaquete
from django.db import models

class Paquete(models.Model):
    legacy_id = models.IntegerField(default=None, blank=True, null=True)
    escuela = models.ForeignKey('Escuela', on_delete=models.CASCADE, related_name='paquetes', default=None, blank=True, null=True)
    fecha_pedido = models.DateField(default=None, blank=True, null=True)
    ne = models.CharField(max_length=512, default=None, blank=True, null=True)
    id_hardware = models.CharField(max_length=512, default=None, blank=True, null=True)
    marca_de_arranque = models.CharField(max_length=512, default=None, blank=True, null=True)
    comentario = models.TextField(max_length=1024, default=None, blank=True, null=True)
    carpeta_paquete = models.CharField(max_length=512, default=None, blank=True, null=True)
    fecha_envio = models.DateField(default=None, blank=True, null=True) # Fecha en que se mandó el pedido a Educar
    zip_paquete = models.CharField(max_length=512, default=None, blank=True, null=True) # Zip con pedido y llaves que se envía por mail a Educar
    estado = models.ForeignKey('EstadoDePaquete', on_delete=models.CASCADE, related_name='paquetes', default=None, blank=True, null=True)
    fecha_devolucion = models.DateField(default=None, blank=True, null=True) # Fecha en que se recibió el paquete solicitado desde Educar
    id_devolucion = models.IntegerField(default=None, blank=True, null=True) # ID que se relaciona con la tabla devoluciones (legacy)
    leido = models.BooleanField(default=False)
    tpmdata = models.BooleanField(default=False)
    ma_hexa = models.CharField(max_length=512, default=None, blank=True, null=True)


    class Meta:
        db_table = 'paquetes'
        verbose_name_plural = "paquetes"
        ordering = ('-fecha_pedido',)

    class JSONAPIMeta:
        resource_name = 'paquetes'

    @classmethod
    def marcar_paquetes_pendientes_como_enviados_a_educar(cls, inicio, fin):
        estado_pendiente = EstadoDePaquete.objects.get(nombre="Pendiente")
        estado_enviado = EstadoDePaquete.objects.get(nombre="EducAr")

        paquetes = Paquete.objects.filter(fecha_pedido__range=(inicio, fin)).filter(estado=estado_pendiente)

        for paquete in paquetes:
            paquete.estado = estado_enviado
            paquete.fecha_envio = datetime.datetime.now().date()
            paquete.save()

    @classmethod
    def cambiar_estado_a_entregado(cls, numero, ruta_a_zip_desde_educar):
        """Busca un paquete con el número indicado, lo cambia de estado
        y almacena el archivo .zip señalado."""

        try:
            paquete = Paquete.objects.get(ma_hexa=numero)
        except Paquete.DoesNotExist:
            print("No se encontro el paquete id={0}".format(numero))
            return False

        if paquete.estado.id is not EstadoDePaquete.objects.get(nombre="EducAr").id:
            print("El paquete id={0} ma_hexa={1} no se puede cambiar a estado Devuelto, porque tiene un estado diferente a EducAr".format(paquete.id, paquete.ma_hexa))
            return False

        """
        TODO: activar especificando dónde guardar el archivo.

        archivo = open(ruta_a_zip_desde_educar)
        archivo_django = ContentFile(archivo.read());
        archivo.close()
        paquete.ruta_archivo.save(archivo_django)
        """

        paquete.estado = EstadoDePaquete.objects.get(nombre="Devuelto")
        paquete.save()

    @classmethod
    def obtener_paquetes_para_exportar(cls, inicio, fin, estadoPedido):
        paquetes = Paquete.objects.filter(fecha_pedido__range=(inicio, fin))

        if estadoPedido != "Todos":
            objeto_estado = EstadoDePaquete.objects.get(nombre=estadoPedido)
            paquetes = paquetes.filter(estado=objeto_estado)

        llaves = set()
        tabla = []

        for paquete in paquetes:
            serie_servidor = "Sin Servidor"
            llave_servidor = ""

            if paquete.escuela:
                cue = paquete.escuela.cue
                escuela = paquete.escuela.nombre

                if paquete.escuela.localidad:
                    region = paquete.escuela.localidad.distrito.region.numero
                    distrito = paquete.escuela.localidad.distrito.nombre
                else:
                    region = "Sin Región"
                    distrito = "Sin Distrito"

                if paquete.escuela.piso:
                    serie_servidor = paquete.escuela.piso.serie

                    if paquete.escuela.piso.llave:
                        llave_servidor = paquete.escuela.piso.llave
                else:
                    serie_servidor = "Sin Servidor"
            else:
                cue = "Sin CUE"
                escuela = "Sin Escuela"
                region = "Sin Región"
                distrito = "Sin Distrito"

            if llave_servidor:
                llaves.add(llave_servidor)

            id_hardware = paquete.id_hardware
            marca_de_arranque = paquete.marca_de_arranque
            ne = paquete.ne
            fecha_pedido = paquete.fecha_pedido
            pedido = fecha_pedido.strftime("%Y-%m-%d")
            estado = paquete.estado.nombre

            tabla.append({
                "cue": cue,
                "escuela": escuela,
                "region": region,
                "distrito": distrito,
                "serie_servidor": serie_servidor,
                "id_hardware": id_hardware,
                "marca_de_arranque": marca_de_arranque,
                "ne": ne,
                "pedido": pedido,
                "estado": estado,
                "llave_servidor": str(llave_servidor),
            })

        data = {
            "inicio": inicio,
            "fin": fin,
            "estadoPedido": estadoPedido,
            "llaves": list(llaves),
            "tabla": tabla
        }

        return data
