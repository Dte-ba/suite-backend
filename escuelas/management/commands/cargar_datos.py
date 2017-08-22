# coding: utf-8
from __future__ import unicode_literals
import time
import datetime

import progressbar
import requests
from openpyxl import load_workbook

from escuelas import models
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

# Esta variable no se debe modificar. Se le puede cambiar el valor en tiempo
# de ejecución invocando el comando "make cargar_datos depuracion=1"
MODO_VERBOSE = False

def log(*k):
    global MODO_VERBOSE

    if MODO_VERBOSE:
        print(k)

BASE_URL = 'http://suite-api.dtelab.com.ar/api/'

def esperar(segundos):
    time.sleep(segundos)

def barra_de_progreso(simple=True):
    if simple:
        return progressbar.ProgressBar(widgets=[progressbar.SimpleProgress()])
    else:
        return progressbar.ProgressBar()

class Command(BaseCommand):
    help = 'Genera todos los datos iniciales.'

    def add_arguments(self, parser):
        parser.add_argument('--filtro', help="Aplica un filtro a los comandos que se ejecutaran")
        parser.add_argument('--depuracion', help="Permite activar todos los detalles (verbose mode)")

    def handle(self, *args, **options):
        global MODO_VERBOSE
        filtro = options['filtro']
        depuracion = options['depuracion']


        # A continuación están todos los comandos que el importador
        # puede ejecutar. Cada comando es un método, con el mismo nombre
        # que aparece como cadena.
        #
        # por ejemplo 'crear_areas' es la orden para ejecutar el método
        # self.crear_areas().
        comandos = [
            'crear_cargos_escolares',
            'crear_regiones',
            'crear_tipos_de_financiamiento',
            'crear_niveles',
            'crear_tipos_de_gestion',
            'crear_areas',
            'crear_programas',
            'crear_cargos',
            'crear_experiencias',
            'crear_contratos',
            'crear_motivos_de_tareas',
            'crear_estados_de_tareas',
            'crear_prioridades_de_tareas',
            'crear_estados_de_validaciones',
            'crear_motivos_de_conformaciones',
            'crear_categorias_de_eventos',
            'crear_estados_de_paquetes',

            'importar_distritos_y_localidades',
            'importar_escuelas',

            'importar_usuarios',

            'importar_contactos',
            'importar_pisos',
            'vincular_programas',
            'importar_tareas',
            'importar_comentarios_de_tareas',
            'importar_eventos',
            'vincular_acompaniantes',
            'importar_conformaciones',
            'importar_validaciones',
            'importar_comentarios_de_validaciones',
            'importar_paquetes',
            'limpiar_e_importar_permisos_con_grupos',
        ]


        print("Procesando comandos a ejecutar ...")
        esperar(1)

        if depuracion != '0':
            print("Modo depuración activado.")
            MODO_VERBOSE = True
        else:
            print("Modo depuración desactivado.")
            MODO_VERBOSE = False

        if filtro:
            print("Aplicando el filtro: " + filtro)
            comandos_filtrados = [x for x in comandos if filtro in x]

            cantidad_de_comandos = len(comandos_filtrados)

            if cantidad_de_comandos == 0:
                print("No hay ningún comando que coincida con el filtro.")
            else:
                print("Solo se ejecutaran %d comandos (de los %d disponibles)" %(cantidad_de_comandos, len(comandos)))
                self.ejecutar_comandos(comandos_filtrados)
        else:
            print("Se ejecutaran %d comandos" %(len(comandos)))
            self.ejecutar_comandos(comandos)

    def ejecutar_comandos(self, comandos):
        esperar(1)
        self.listar_comandos(comandos)
        esperar(2)

        for x in comandos:
            metodo = getattr(self, x)
            metodo()

    def listar_comandos(self, comandos):
        print("Se ejecutarán los comandos en este orden:")
        for i, x in enumerate(comandos):
            print ("  %d %s" %(i+1, x))

    def crear_regiones(self):
        numeros = range(1, 26)

        print("Creando Regiones")
        bar = barra_de_progreso()

        for n in bar(numeros):
            p, created = models.Region.objects.get_or_create(numero=n)
            log(p)

        p, created = models.Region.objects.get_or_create(numero=27)

        if MODO_VERBOSE:
            print(p)

    def importar_distritos_y_localidades(self):
        localidades = self.obtener_datos_desde_api('localidades')['localidades']

        print("Creando Localidades")
        bar = barra_de_progreso(simple=False)

        for localidad in bar(localidades):
            objeto_distrito, Localidadescreated = models.Distrito.objects.get_or_create(nombre=localidad['distrito'].title())
            objeto_localidad, created = models.Localidad.objects.get_or_create(nombre=localidad['localidad'].title())

            objeto_localidad.distrito = objeto_distrito
            objeto_localidad.save()

            objeto_distrito.region, created = models.Region.objects.get_or_create(numero=int(localidad['region']))
            objeto_distrito.save()

            if MODO_VERBOSE:
                print objeto_distrito, " -> ", objeto_localidad, "de la", objeto_distrito.region

    def importar_eventos(self):
        eventos = self.obtener_datos_desde_api('eventos')['eventos']

        print("Creando Eventos")
        bar = barra_de_progreso(simple=False)

        for evento in bar(eventos):
            legacy_id = evento['legacy_id']
            fecha_inicio = evento['fecha_inicio']
            hora_inicio = evento['hora_inicio']
            fecha_final = evento['fecha_final']
            hora_final = evento['hora_final']
            fecha_carga = evento['fecha_de_carga']
            cue = evento['cue']
            #responsable = evento['usuario']
            dni_usuario = evento['dni_usuario']
            objetivo = evento['objetivo']
            cantidad_de_participantes = evento['cantidad_de_participantes']
            #minuta = evento['minuta']
            acta = evento['acta']
            categoria = evento['categoria']
            subcategoria = evento['subcategoria']
            titulo = categoria + " " + subcategoria

            if MODO_VERBOSE:
                print "Se intenta buscar evento asociado a cue: " + str(cue)

            objeto_evento, created = models.Evento.objects.get_or_create(legacy_id=legacy_id)

            try:
                objeto_responsable = models.Perfil.objects.get(dni=dni_usuario)
            except models.Perfil.DoesNotExist:
                log("Error, no existe registro de usuario buscado %s. No se registrará el evento." %(dni_usuario))
                # cantidad_de_tareas_omitidas += 1
                continue

            try:
                objeto_escuela = models.Escuela.objects.get(cue=cue)
            except models.Escuela.DoesNotExist:
                log("Error, no existe la escuela buscada con cue %s. No se registrará el evento." %(cue))
                # cantidad_de_comentarios_de_tareas_omitidos += 1
                continue

            objeto_evento.titulo = titulo
            objeto_evento.fecha = fecha_inicio
            objeto_evento.inicio = hora_inicio
            objeto_evento.fecha_fin = fecha_final
            objeto_evento.fin = hora_final
            objeto_evento.responsable = objeto_responsable
            objeto_evento.escuela = objeto_escuela
            objeto_evento.save()


            if MODO_VERBOSE:
                print "=============================="
                print "   SE HA CREADO EL REGISTRO   "
                print "=============================="
                print "legacy_id:               " + str(legacy_id)
                print "Titulo:                  " + titulo
                print "Inicio:                  " + fecha_inicio + " " + hora_inicio
                print "Fin:                     " + fecha_final + " " + hora_final
                print "Categoria:               " + categoria
                print "Subcategoria:            " + subcategoria
                print "Objetivo:                " + objetivo
                print "Acta:                    " + acta
                print "Responsable:             " + objeto_responsable.apellido + ", " + objeto_responsable.nombre + " (dni " + dni_usuario + ")"
                print "Fecha de creacion:       " + fecha_carga
                print "Cant. de Participantes:  " + str(cantidad_de_participantes)
                print "Escuela:                 " + objeto_escuela.nombre + " " + str(cue)
                print "=============================="

    def importar_escuelas(self):
        resultado = self.obtener_datos_desde_api('escuelas')

        print("Se importarán %d escuelas en total." %(resultado['cantidad']))
        esperar(2)

        escuelas = resultado['escuelas']

        bar = barra_de_progreso(simple=False)

        for escuela in bar(escuelas):

            if MODO_VERBOSE:
                print "Intentando crear el registro escuela id_original:", escuela['id']

            objeto_escuela, created = models.Escuela.objects.get_or_create(cue=escuela['cue'])

            objeto_area, created = models.Area.objects.get_or_create(nombre=escuela['area'].title())

            objeto_localidad, created = models.Localidad.objects.get_or_create(nombre=escuela['localidad'].title())
            objeto_tipoDeFinanciamiento, created = models.TipoDeFinanciamiento.objects.get_or_create(nombre=escuela['tipo_financiamiento'].title())
            objeto_nivel, created = models.Nivel.objects.get_or_create(nombre=escuela['nivel'].title())
            objeto_tipoDeGestion, created = models.TipoDeGestion.objects.get_or_create(nombre=escuela['tipo_gestion'].title())
            #objeto_programa, created = models.Programa.objects.get_or_create(nombre=escuela['programa'].title())

            objeto_escuela.nombre = escuela['nombre'].title()
            objeto_escuela.direccion = escuela['direccion']
            objeto_escuela.telefono = escuela['telefono']
            objeto_escuela.latitud = escuela['latitud']
            objeto_escuela.longitud = escuela['longitud']

            objeto_escuela.area = objeto_area

            objeto_escuela.localidad = objeto_localidad
            objeto_escuela.tipoDeFinanciamiento = objeto_tipoDeFinanciamiento
            objeto_escuela.nivel = objeto_nivel
            objeto_escuela.tipoDeGestion = objeto_tipoDeGestion
            #objeto_escuela.programas = objeto_programa

            objeto_escuela.estado = True

            objeto_escuela.save()

            log("Se ha creado el registro:")
            log(objeto_escuela, "\n CUE: ", objeto_escuela.cue, "\n Direccion: ", objeto_escuela.direccion, "\n Tel: ", objeto_escuela.telefono, "\n ", objeto_escuela.localidad, "\n ", objeto_escuela.area, "\n ", objeto_escuela.nivel, "\n ", objeto_escuela.tipoDeFinanciamiento, "\n ", objeto_escuela.tipoDeGestion)
            log("===========")

    def importar_usuarios(self):
        ARCHIVO = './/archivos_para_importacion/dte_perfiles_2017.xlsx'
        LIMITE_DE_FILAS = 300

        print("Comenzando la importación de usuarios")
        log("Iniciando la importación del archivo: " + ARCHIVO)
        wb = load_workbook(ARCHIVO)

        columnas_como_string = ", ".join(wb.get_sheet_names())
        log("Las páginas de la planilla son: " + columnas_como_string)

        filas_procesadas = 0
        filas_omitidas_o_con_errores = 0
        filas_omitidas_lista = ""

        def formatear_fecha(fecha):
            if fecha:
                return fecha.strftime('%Y-%m-%d')
            else:
                return fecha

        def obtener_valores_desde_fila(fila):
            return {
                "region":               fila[0].value,
                "cargo":                fila[1].value,
                "contrato":             fila[2].value,
                "carga_horaria":        fila[3].value,
                "consultor":            fila[4].value.strip().capitalize(),
                # "documentacion":        fila[5].value, # En principio, no nos interesa este dato.
                "expediente":           fila[6].value,
                "fechaDeRenuncia":      fila[7].value,
                "titulo":               fila[8].value,
                "fechaDeIngreso":       fila[9].value,
                "perfil":               fila[10].value,
                "dni":                  fila[11].value,
                "cuil":                 fila[12].value,
                "cbu":                  fila[13].value,
                "email":                fila[14].value,
                "email_laboral":        fila[15].value,
                "direccion":            fila[16].value,
                "localidad":            fila[17].value,
                "codigo_postal":        fila[18].value,
                "fechaDeNacimiento":    fila[19].value,
                "telefono_celular":     fila[20].value,
                "telefono_particular":  fila[21].value,
                "telefono_alternativo": fila[22].value,
            }

        bar = barra_de_progreso(simple=False)
        #for conformacion in bar(conformaciones):

        for indice, fila in bar(enumerate(wb.active.rows)):

            if indice is 0:
                continue;             # Ignora la cabecera

            if not fila[1].value:
                log("Terminando en la fila %d porque no parece haber mas registros." %(indice + 1))
                break

            log("Procesando fila '%d'" %(indice +1))

            try:
                valores = obtener_valores_desde_fila(fila)

                if valores['fechaDeRenuncia']:
                    log("Renunció")
                    fechaDeRenuncia=formatear_fecha(valores['fechaDeRenuncia'])
                else:
                    log("Perfil activo")
                    fechaDeRenuncia=None

                region=str(valores['region'])

                if region=="ESP/NC" or region=="NC" or region=="Nc" or region=="NC Esp" or region=="NC Prov." or region=="NC Sup" or region=="NC. Prov":
                    region="27"

                cargo=valores['cargo']
                contrato=valores['contrato']
                carga_horaria=valores['carga_horaria']
                consultor=valores['consultor'].split(',')
                apellido=consultor[0]
                nombre=consultor[1].title()

                if valores['expediente']:
                    log("No tiene expediente")
                    expediente=valores['expediente']
                else:
                    expediente="Sin Datos"

                if valores['titulo']:
                    titulo=valores['titulo']
                else:
                    log("No tiene título")
                    titulo="Sin Datos"

                fechaDeIngreso=formatear_fecha(valores['fechaDeIngreso'])

                if valores['perfil']:
                    experiencia=valores['perfil']
                else:
                    log("No tiene perfil")
                    experiencia="Sin Datos"

                dni = str(valores['dni'])

                if valores['cuil']:
                    cuil=str(valores['cuil'])
                else:
                    log("No tiene CUIL")
                    cuil="Sin Datos"

                if valores['cbu']:
                    cbu=valores['cbu']
                else:
                    log("No tiene cbu")
                    cbu="Sin Datos"

                if valores['email']:
                    email=valores['email']
                else:
                    log("No tiene email")
                    email="Sin Datos"

                if valores['email_laboral']:
                    email_laboral=valores['email_laboral']
                else:
                    log("No tiene email laboral")
                    email_laboral=apellido+"@abc.gob.ar"

                email_laboral = email_laboral.lower()

                if valores['direccion']:
                    direccion=valores['direccion']
                else:
                    log("No tiene direccion")
                    direccion="Sin Datos"

                localidad=valores['localidad'].title()
                codigo_postal=str(valores['codigo_postal'])

                if valores['fechaDeNacimiento']:
                    fechaDeNacimiento=formatear_fecha(valores['fechaDeNacimiento'])
                else:
                    log("No tiene fecha de nacimiento")
                    fechaDeNacimiento=None

                if valores['telefono_celular']:
                    telefono_celular=valores['telefono_celular']
                else:
                    log("No tiene telefono celular")
                    telefono_celular="Sin Datos"

                if valores['telefono_particular']:
                    log("No tiene telefono Particular")
                    telefono_particular=valores['telefono_particular']
                else:
                    telefono_particular="Sin Datos"

                username=email_laboral
                default_pass="dte_"+dni


                try:
                    user = User.objects.get(username=email_laboral)
                except User.DoesNotExist:
                    user = User(username=email_laboral, email=email)
                    user.set_password(default_pass)

                user.save()

                perfil = models.Perfil.objects.get(user=user)

                perfil.nombre = nombre
                perfil.apellido = apellido
                perfil.fechadenacimiento = fechaDeNacimiento
                perfil.titulo = titulo
                perfil.dni = dni
                perfil.cuit = cuil
                perfil.cbu = cbu
                perfil.email = email
                perfil.direccionCalle = direccion
                perfil.codigoPostal = codigo_postal
                perfil.telefonoCelular = telefono_celular
                perfil.telefonoAlternativo = telefono_particular
                perfil.expediente = expediente
                perfil.fechaDeIngreso = fechaDeIngreso
                perfil.fechaDeRenuncia = fechaDeRenuncia
                perfil.emailLaboral = email_laboral

                perfil.region = models.Region.objects.get(numero=int(region))
                # perfil.experiencia = models.Experiencia.objects.get(nombre=experiencia)
                # perfil.localidad = models.Localidad.objects.get(nombre=localidad)
                perfil.cargo = models.Cargo.objects.get(nombre=cargo)
                perfil.contrato = models.Contrato.objects.get(nombre=contrato)

                perfil.save()
            except TypeError, e:
                log("-----")
                log("Fila %d - ****** OMITIDA, TypeError. La fila contiene caracteres incorrectos." %(indice + 1))
                filas_omitidas_o_con_errores += 1
                filas_omitidas_lista += ", " + str(indice + 1)
                log(e)
                log("-----")
                continue

            log("Fila %d - Cargando datos de perfil para consultor: '%s'" %(indice + 1, valores["consultor"]))
            log("")
            log("Apellido: " + apellido)
            log("Nombres: " + nombre)
            log("Region: " + region)
            log("Cargo: " + cargo)
            log("Contrato: " + contrato)
            log("Carga horaria: " + carga_horaria)
            log("Expediente: " + expediente)
            #log("Fecha de Ingreso: " + fechaDeIngreso)
            # log("Fecha de Renuncia: " + fechaDeRenuncia)
            log("Titulo: " + titulo)
            log("Perfil: " + experiencia)
            log("DNI: " + dni)
            log("CUIL: " + cuil)
            log("CBU: " + cbu)
            log("Email: " + email)
            log("Email Laboral: " + email_laboral)
            log("Direccion: " + direccion)
            log("Localidad: " + localidad)
            log("Codigo Postal: " + codigo_postal)
            #log("Fecha de nacimiento: " + fechaDeNacimiento)
            log("Telefono Celular: " + telefono_celular)
            log("Telefono Particular: " + telefono_particular)
            log("Username: " + username)
            log("Password: " + default_pass)
            log("-----")
            log("")

            filas_procesadas += 1

            if indice > LIMITE_DE_FILAS:
                break


        log("Terminó la ejecución")

        log("")
        log("Resumen:")
        log("")
        log(" - cantidad total de filas:                       " + str(indice - 1))
        log(" - filas procesadas:                              " + str(filas_procesadas))
        log(" - cantidad de filas que fallaron:                " + str(indice - 1 - filas_procesadas))

        log(" - filas que fallaron:                            " + str(filas_omitidas_lista))
        # log(" - filas con error u omitidas:                    " + str(filas_omitidas_o_con_errores))
        # log(" - cantidad de socios sin grupo familiar:         " + str(cantidad_de_socios_sin_grupo_familiar))
        # log(" - cantidad de perfiles que renunciaron: " + str(cantidad_de_perfiles_con_renuncia))
        log("")
        log("")


    def importar_conformaciones(self):
        resultado = self.obtener_datos_desde_api('conformaciones')

        print("Se importarán %d conformaciones en total." %(resultado['cantidad']))
        esperar(2)

        conformaciones = resultado['conformaciones']

        bar = barra_de_progreso(simple=False)

        for conformacion in bar(conformaciones):

            cue_conformado = conformacion['cue_conformado']
            cue_principal = conformacion['cue_principal']
            motivo = conformacion['motivo']
            fecha = conformacion['fecha']

            if MODO_VERBOSE:
                print "Intentando crear conformacion de escuela `", cue_conformado, "` con la escuela padre ", cue_principal, " y motivo ", motivo
                print "======================================================================================================"
                print "Escuela ", cue_conformado, " queda conformada con padre ", cue_principal
                print "Fecha:   ", fecha
                print "Motivo:  ", motivo
                print "======================================================================================================"

            objeto_escuela = models.Escuela.objects.get(cue=cue_conformado)
            escuela_padre = models.Escuela.objects.get(cue=cue_principal)
            objeto_motivo = models.MotivoDeConformacion.objects.get(nombre=motivo)
            fecha_como_objeto = datetime.datetime.strptime(fecha, "%Y-%m-%d")

            if objeto_escuela.padre != escuela_padre:
                escuela_padre.conformar_con(objeto_escuela, objeto_motivo, fecha_como_objeto)
                
            objeto_escuela.save()

    def importar_paquetes(self):
        resultado = self.obtener_datos_desde_api('paquetes')

        cantidad_de_paquetes_creados = 0
        cantidad_de_paquetes_omitidos = 0
        cantidad_de_paquetes_sin_escuela = 0

        print("Se importarán %d paquetes de provisión en total." %(resultado['cantidad']))
        esperar(2)

        paquetes = resultado['paquetes']

        bar = barra_de_progreso(simple=False)

        for paquete in bar(paquetes):

            legacy_id = paquete['legacy_id']
            cue = paquete['cue']
            ne = paquete['ne']
            servidor_serie = paquete['servidor_serie']
            idhardware = paquete['idhardware']
            marca_de_arranque = paquete['marca_de_arranque']
            llave_servidor = paquete['llave_servidor']
            fecha_pedido = paquete['fecha_pedido']
            comentario = paquete['comentario']
            carpeta_paquete = paquete['carpeta_paquete']
            fecha_envio_anses = paquete['fecha_envio_anses']
            zipanses = paquete['zipanses']
            estado = paquete['estado']
            fecha_devolucion = paquete['fecha_devolucion']
            leido = paquete['leido']


            if MODO_VERBOSE:
                print "======================================================================================================"
                print "Intentando crear paquete de provisión para el cue ", cue
                print "======================================================================================================"
                print "legacy_id", legacy_id
                print "CUE ", cue
                print "Fecha de pedido:", fecha_pedido
                print "NE:  ", ne
                print "Servidor:  ", servidor_serie
                print "idhardware:  ", idhardware
                print "marca_de_arranque:  ", marca_de_arranque
                print "Llave del servidor:  ", llave_servidor
                print "Comentario:  ", comentario
                print "Carpeta del paquete:  ", carpeta_paquete
                print "Fecha de envío a ANSES:  ", fecha_envio_anses
                print "ZIP ANSES:  ", zipanses
                print "Estado:  ", estado
                print "Fecha de devolición:  ", fecha_devolucion
                print "Leido:  ", leido
                print "======================================================================================================"

            try:
                objeto_escuela = models.Escuela.objects.get(cue=cue)
            except models.Escuela.DoesNotExist:
                log("Error, no existe la escuela con cue %s. Se ignora el registro." %(cue))
                cantidad_de_paquetes_omitidos += 1
                cantidad_de_paquetes_sin_escuela += 1
                continue

            if estado == 0:
                estado = "Objetado"
            elif estado == 1:
                estado = "Pendiente"
            elif estado == 2:
                estado = "EducAr"
            elif estado == 3:
                estado = "Devuelto"
            else:
                estado = "Descargado"

            objeto_estado = models.EstadoDePaquete.objects.get(nombre=estado)

            if leido == 0:
                leido = False
            else:
                leido = True

            if fecha_envio_anses == "0000-00-00":
                fecha_envio_anses = None

            objeto_paquete, created = models.Paquete.objects.get_or_create(legacy_id=legacy_id)
            objeto_paquete.escuela = objeto_escuela
            objeto_paquete.fechaPedido = fecha_pedido
            objeto_paquete.ne = ne
            objeto_paquete.idHardware = idhardware
            objeto_paquete.marcaDeArranque = marca_de_arranque
            objeto_paquete.comentario = comentario
            objeto_paquete.carpetaPaquete = carpeta_paquete
            objeto_paquete.fechaEnvio = fecha_envio_anses
            objeto_paquete.zipPaquete = zipanses
            objeto_paquete.estado = objeto_estado
            objeto_paquete.fechaDevolucion = fecha_devolucion
            objeto_paquete.leido = leido

            objeto_paquete.save()

            cantidad_de_paquetes_creados += 1

        print("Resumen de paquetes:")
        print("   Se crearon %d paquetes correctamente." %(cantidad_de_paquetes_creados))
        print("   Se evitaron crear %d paquetes:" %(cantidad_de_paquetes_omitidos))
        print("     No se encontró la escuela de %s paquetes:" %(cantidad_de_paquetes_sin_escuela))


    def importar_validaciones(self):
        resultado = self.obtener_datos_desde_api('validaciones')
        cantidad_de_validaciones_creadas = 0
        cantidad_de_validaciones_omitidas = 0
        cantidad_de_validaciones_sin_escuela = 0
        cantidad_de_validaciones_sin_usuario = 0
        cantidad_de_validaciones_con_motivo_erroneo = 0

        print("Se importarán %d validaciones en total." %(resultado['cantidad']))
        esperar(2)

        validaciones = resultado['validaciones']

        bar = barra_de_progreso(simple=False)

        for validacion in bar(validaciones):

            legacy_id = validacion['legacy_id']
            cue = validacion['cue']
            escuela = validacion['escuela']
            dni_usuario = validacion['dni_usuario']
            usuario = validacion['usuario']
            estado = validacion['estado']
            fecha = validacion['fecha_de_alta']

            if estado==1:
                estado = "Pendiente"
            elif estado==2:
                estado = "Objetada"
            elif estado==3:
                estado = "Aprobada"
            else:
                estado = "NO IMPORTAR"

            if MODO_VERBOSE:
                print "Intentando crear validacion con legacy_id ", legacy_id, " y estado ", estado
                print "======================================================================================================"
                print "Escuela ", escuela, "  ", cue
                print "Usuario: ", usuario, " (", dni_usuario, ")"
                print "Fecha:   ", fecha
                print "Estado:  ", estado
                print "======================================================================================================"


            try:
                objeto_escuela = models.Escuela.objects.get(cue=cue)
            except models.Escuela.DoesNotExist:
                log("Error, no existe la escuela con cue %s. Se ignora el registro." %(cue))
                cantidad_de_validaciones_omitidas += 1
                cantidad_de_validaciones_sin_escuela += 1
                continue

            try:
                objeto_usuario = models.Perfil.objects.get(dni=dni_usuario)
            except models.Perfil.DoesNotExist:
                log("Error, no existe el usuario con dni %s. Se ignora el registro." %(dni_usuario))
                cantidad_de_validaciones_omitidas += 1
                cantidad_de_validaciones_sin_usuario += 1
                continue



            try:
                objeto_estado = models.EstadoDeValidacion.objects.get(nombre=estado)
            except models.EstadoDeValidacion.DoesNotExist:
                log("Error, estado %s no corresponde. Se ignora el registro." %(estado))
                cantidad_de_validaciones_omitidas += 1
                cantidad_de_validaciones_con_motivo_erroneo += 1
                continue


            objeto_validacion, created = models.Validacion.objects.get_or_create(legacy_id=legacy_id)
            objeto_validacion.fechaDeAlta = fecha
            objeto_validacion.autor = objeto_usuario
            objeto_validacion.estado = objeto_estado
            objeto_validacion.escuela = objeto_escuela

            objeto_validacion.save()

            cantidad_de_validaciones_creadas += 1

        print("Resumen de validaciones:")
        print("   Se crearon %d validaciones correctamente." %(cantidad_de_validaciones_creadas))
        print("   Se evitaron crear %d validaciones:" %(cantidad_de_validaciones_omitidas))
        print("     No se encontró la escuela de %s validaciones:" %(cantidad_de_validaciones_sin_escuela))
        print("     No se encontró el usuario de %s validaciones:" %(cantidad_de_validaciones_sin_usuario))
        print("     Hay %s validaciones con estado erróneo:" %(cantidad_de_validaciones_con_motivo_erroneo))

    def importar_comentarios_de_validaciones(self):
        resultado = self.obtener_datos_desde_api('historial_validaciones')
        cantidad_de_validaciones_creadas = 0
        cantidad_de_validaciones_omitidas = 0
        #cantidad_de_validaciones_sin_escuela = 0
        cantidad_de_validaciones_sin_usuario = 0
        cantidad_de_validaciones_con_motivo_erroneo = 0

        print("Se importarán %d comentarios de validaciones en total." %(resultado['cantidad']))
        esperar(2)

        comentarios = resultado['historial_validaciones']

        bar = barra_de_progreso(simple=False)

        for comentario in bar(comentarios):

            cantidad = comentario['cantidad']
            usuario = comentario['usuario']
            dni_usuario = comentario['dni_usuario']
            fecha = comentario['fecha']
            legacy_id = comentario['legacy_id']
            validacion = comentario['validacion_legacy_id']
            comentario = comentario['observaciones']

            if MODO_VERBOSE:
                print "Intentando crear comentario de validacion con legacy_id ", legacy_id
                print "======================================================================================================"
                print "ID Validacion:", validacion
                print "Usuario: ", usuario, " (", dni_usuario, ")"
                print "Fecha:   ", fecha
                print "Comentario:  ", comentario
                print "======================================================================================================"


            try:
                objeto_usuario = models.Perfil.objects.get(dni=dni_usuario)
            except models.Perfil.DoesNotExist:
                log("Error, no existe el usuario con dni %s. Se ignora el registro." %(dni_usuario))
                cantidad_de_validaciones_omitidas += 1
                cantidad_de_validaciones_sin_usuario += 1
                continue

            try:
                objeto_validacion = models.Validacion.objects.get(legacy_id=validacion)
            except models.Validacion.DoesNotExist:
                log("Error, no existe la validacion con legacy_id %s. Se ignora el registro." %(validacion))
                cantidad_de_validaciones_omitidas += 1
                cantidad_de_validaciones_con_motivo_erroneo += 1
                continue


            objeto_comentario_de_validacion, created = models.ComentarioDeValidacion.objects.get_or_create(legacy_id=legacy_id)
            objeto_comentario_de_validacion.validacion = objeto_validacion
            objeto_comentario_de_validacion.fecha = fecha
            objeto_comentario_de_validacion.autor = objeto_usuario
            objeto_comentario_de_validacion.comentario = comentario
            objeto_comentario_de_validacion.cantidad = cantidad

            objeto_comentario_de_validacion.save()

            cantidad_de_validaciones_creadas += 1

        print("Resumen de comentarios de validaciones:")
        print("   Se crearon %d comentarios correctamente." %(cantidad_de_validaciones_creadas))
        print("   Se evitaron crear %d comentarios:" %(cantidad_de_validaciones_omitidas))
        print("     No se encontró la validacion correspondiente a %s comentarios:" %(cantidad_de_validaciones_con_motivo_erroneo))
        print("     No se encontró el usuario de %s comentarios:" %(cantidad_de_validaciones_sin_usuario))


    def importar_contactos(self):
        contactos = self.obtener_datos_desde_api('contactos')['contactos']

        print("Importando Contactos")
        bar = barra_de_progreso(simple=False)

        for contacto in bar(contactos):
            log("Buscando escuela para el contacto: ", contacto['escuela'])
            objeto_escuela = models.Escuela.objects.get(cue=contacto['escuela'])
            objeto_cargo = models.CargoEscolar.objects.get(nombre=contacto['cargo'])
            objeto_contacto, created = models.Contacto.objects.get_or_create(nombre=contacto['nombre'].title())
            #
            objeto_contacto.cargo = objeto_cargo
            objeto_contacto.escuela = objeto_escuela
            if contacto['email']:
                objeto_contacto.email = contacto['email'].lower()

            objeto_contacto.telefono_particular = contacto['telefono']
            objeto_contacto.telefono_celular = contacto['celular']
            if contacto['horario']:
                objeto_contacto.horario = contacto['horario'].title()

            objeto_contacto.save()

            log("Se ha creado el registro:")
            log("Nombre: ", objeto_contacto, "\n Teléfono Particular ", objeto_contacto.telefono_particular, "\n Teléfono Celular: ", objeto_contacto.telefono_celular, "\n Email: ", objeto_contacto.email, "\n Horario: ", objeto_contacto.horario)
            log("===========")

    def importar_pisos(self):
        pisos = self.obtener_datos_desde_api('pisos')['pisos']

        print("Importando Pisos")
        bar = barra_de_progreso(simple=False)

        for piso in bar(pisos):

            if piso['marca']:
                marca = piso['marca']
            else:
                marca = "Desconocido"

            log("Buscando piso para escuela: ", piso['cue'])
            objeto_escuela = models.Escuela.objects.get(cue=piso['cue'])
            objeto_piso, created = models.Piso.objects.get_or_create(legacy_id=piso['legacy_id'])
            #
            objeto_piso.servidor = piso['marca']
            objeto_piso.serie = piso['serie']

            if piso['ups']:
                if piso['ups'] == "SI":
                    objeto_piso.ups = True
                else:
                    objeto_piso.ups = False
            else:
                objeto_piso.ups = False


            if piso['rack']:
                if piso['rack'] == "SI":
                    objeto_piso.rack = True
                else:
                    objeto_piso.rack = False
            else:
                objeto_piso.rack = False

            objeto_piso.estado = piso['piso_estado']

            objeto_escuela.piso = objeto_piso

            objeto_piso.save()
            objeto_escuela.save()

            log("Se ha creado el registro:")
            log("Piso de escuela ", piso['cue'], ": \n Servidor: ", piso['marca'], "\n Serie: ", piso['serie'], "\n UPS: ", piso['ups'], "\n Rack: ", piso['rack'], "\n Estado: ", piso['piso_estado'])
            log("===========")

    def importar_tareas(self):
        tareas = self.obtener_datos_desde_api('tickets')['tickets']
        cantidad_de_tareas_creadas = 0
        cantidad_de_tareas_omitidas = 0

        print("Importando Tareas")
        bar = barra_de_progreso(simple=False)

        for tarea in bar(tareas):
            log("Se intenta crear el registro con id_original: " + str(tarea['id_ticket_original']) + " y DNI de usuario: " + str(tarea['dni_usuario']))
            log("Prioridad de la tarea: " + str(tarea['prioridad']))
            log("Motivo de la tarea: " + unicode(tarea['motivo']))
            log("Estado de la tarea: " + str(tarea['estado']))

            dni_usuario = tarea['dni_usuario']

            try:
                objeto_autor = models.Perfil.objects.get(dni=dni_usuario)
            except models.Perfil.DoesNotExist:
                log("Error, no existe registro de usuario buscado %s. No se registrará la tarea." %(dni_usuario))
                cantidad_de_tareas_omitidas += 1
                continue

            objeto_tarea, created = models.Tarea.objects.get_or_create(id_ticket_original=tarea['id_ticket_original'])

            objeto_escuela = models.Escuela.objects.get(cue=tarea['cue'])
            objeto_motivo = models.MotivoDeTarea.objects.get(nombre=tarea['motivo'])
            objeto_estado = models.EstadoDeTarea.objects.get(nombre=tarea['estado'])

            prioridad = tarea['prioridad']
            if prioridad == 1:
                prioridad = "Alta"
            elif prioridad == 2:
                prioridad = "Media"
            elif prioridad == 3:
                prioridad = "Baja"

            objeto_prioridad = models.PrioridadDeTarea.objects.get(nombre=prioridad)

            fecha_alta = tarea['fecha_alta']
            #
            objeto_tarea.fechaDeAlta = fecha_alta
            objeto_tarea.titulo = "Tarea #: " + str(tarea['id_ticket_original'])
            objeto_tarea.descripcion = tarea['descripcion']
            objeto_tarea.autor = objeto_autor
            objeto_tarea.escuela = objeto_escuela
            objeto_tarea.motivoDeTarea = objeto_motivo
            objeto_tarea.estadoDeTarea = objeto_estado
            objeto_tarea.prioridadDeTarea = objeto_prioridad

            objeto_tarea.save()


            log("Se ha creado el registro:")
            log("Tarea con id_original: " + str(tarea['id_ticket_original']))
            log("===========")
            cantidad_de_tareas_creadas += 1

        print("Resumen de tareas:")
        print("   Se crearon %d tareas correctamente." %(cantidad_de_tareas_creadas))
        print("   Se evitaron crear %d tareas porque correspondían a usuarios inexistentes." %(cantidad_de_tareas_omitidas))

    def importar_comentarios_de_tareas(self):
        comentarios = self.obtener_datos_desde_api('comentarios_tickets')['comentarios_tickets']
        cantidad_de_comentarios_de_tareas_creados = 0
        cantidad_de_comentarios_de_tareas_omitidos = 0

        print("Importando Comentarios de Tareas")
        bar = barra_de_progreso(simple=False)

        for comentario in bar(comentarios):
            log("Se intenta crear el registro con id_original: " + str(comentario['id_ticket_original']) + " y DNI de usuario: " + str(comentario['dni_usuario']))

            dni_usuario = comentario['dni_usuario']
            id_ticket_original = comentario['id_ticket_original']

            try:
                objeto_autor = models.Perfil.objects.get(dni=dni_usuario)
            except models.Perfil.DoesNotExist:
                log("Error, no existe registro de usuario buscado %s. No se registrará la tarea." %(dni_usuario))
                cantidad_de_comentarios_de_tareas_omitidos += 1
                continue

            try:
                objeto_tarea = models.Tarea.objects.get(id_ticket_original=id_ticket_original)
            except models.Tarea.DoesNotExist:
                log("Error, no existe registro de tarea buscado %s. No se registrará el comentario." %(id_ticket_original))
                cantidad_de_comentarios_de_tareas_omitidos += 1
                continue



            objeto_comentario, created = models.ComentarioDeTarea.objects.get_or_create(comentario=comentario['comentario'])
            objeto_comentario.autor = objeto_autor
            objeto_comentario.fechaDeAlta = comentario['fecha']
            objeto_comentario.tarea = objeto_tarea

            objeto_comentario.save()


            log("Se ha creado el registro:")
            log("Comentario de Tarea con id_original: " + str(comentario['id_ticket_original']))
            log("===========")
            cantidad_de_comentarios_de_tareas_creados += 1

        print("Resumen de tareas:")
        print("   Se crearon %d comentarios de tareas correctamente." %(cantidad_de_comentarios_de_tareas_creados))
        print("   Se evitaron crear %d comentarios de tareas porque correspondían a usuarios inexistentes." %(cantidad_de_comentarios_de_tareas_omitidos))

    def vincular_programas(self):
        programas = self.obtener_datos_desde_api('programas')['programas']

        print("Vinculando Programas")
        bar = barra_de_progreso(simple=False)

        for programa in bar(programas):
            log("Busando programas para escuela: ", programa['cue'])

            objeto_escuela = models.Escuela.objects.get(cue=programa['cue'])

            objeto_escuela.programas.add(models.Programa.objects.get(nombre=programa['programa']))

            objeto_escuela.save()

            log("Se ha vinculado el registro:")
            log("Programa: ", programa['programa'], "a la escuela con CUE ", programa['cue'])
            log("===========")

    def vincular_acompaniantes(self):
        acompaniantes = self.obtener_datos_desde_api('acompaniantes_eventos')['acompaniantes_eventos']

        print("Vinculando Acompañantes de eventos")
        bar = barra_de_progreso(simple=False)

        for acompaniante in bar(acompaniantes):

            legacy_id = acompaniante['legacy_id']
            dni_usuario = acompaniante['dni_usuario']

            log("Busando acompaniantes para legacy_id: ", legacy_id)

            try:
                objeto_evento = models.Evento.objects.get(legacy_id=legacy_id)
            except models.Evento.DoesNotExist:
                log("Error, no existe registro de evento con legacy_id %s. No se registrará el acompañante." %(legacy_id))
                # cantidad_de_comentarios_de_tareas_omitidos += 1
                continue

            try:
                models.Perfil.objects.get(dni=dni_usuario)
            except models.Perfil.DoesNotExist:
                log("Error, no existe registro de usuario buscado %s. No se registrará el acompañante." %(dni_usuario))
                # cantidad_de_tareas_omitidas += 1
                continue

            objeto_evento.acompaniantes.add(models.Perfil.objects.get(dni=dni_usuario))

            objeto_evento.save()

            log("Se ha vinculado el registro:")
            log("Acomaniante: ", acompaniante['nombre'], "al evento con legacy_id ", acompaniante['legacy_id'])
            log("===========")

    def obtener_datos_desde_api(self, data):
        url = BASE_URL + data
        print("Consultando la URL: " + url)
        resultado = requests.get(url)
        return resultado.json()

    def crear_tipos_de_financiamiento(self):
        nombres = ["Nacional", "Provincial", "Municipal", "Propio"]

        print("Creando Tipos de Financiamiento")
        bar = barra_de_progreso()

        for nombre in bar(nombres):
            p, created = models.TipoDeFinanciamiento.objects.get_or_create(nombre=nombre)
            log(p)

    def crear_estados_de_paquetes(self):
        nombres = ["Objetado", "Pendiente", "EducAr", "Devuelto", "Descargado"]

        print("Creando Estados de Paquetes")
        bar = barra_de_progreso()

        for nombre in bar(nombres):
            p, created = models.EstadoDePaquete.objects.get_or_create(nombre=nombre)
            log(p)

    def crear_motivos_de_tareas(self):
        nombres = [
            "Servidor robado",
            "Servidor roto",
            "Piso tecnológico",
            "Paquetes de provisión",
            "Movimiento de equipamiento",
            "Problemas eléctricos",
            "Switch roto",
            "UPS roto",
            "Mantenimiento básico de piso",
            "Ampliacion de piso",
            "Reingeniería de piso",
            "Mudanza de piso",
            "Reclamos del territorio"
        ]

        print("Creando Motivos de Tareas")
        bar = barra_de_progreso()

        for nombre in bar(nombres):
            p, created = models.MotivoDeTarea.objects.get_or_create(nombre=nombre)
            log(p)

    def crear_motivos_de_conformaciones(self):
        nombres = [
            "Comparte Piso",
            "Comparte Edificio",
            "CUE Nuevo",
            "CUE Anterior",
            "Se Unificó"
        ]

        print("Creando Motivos de Conformaciones")
        bar = barra_de_progreso()

        for nombre in bar(nombres):
            p, created = models.MotivoDeConformacion.objects.get_or_create(nombre=nombre)
            log(p)

    def crear_estados_de_tareas(self):
        nombres = [
            "Abierto",
            "En Progreso",
            "En Espera",
            "Cerrado"
        ]

        print("Creando Estados de Tareas")
        bar = barra_de_progreso()

        for nombre in bar(nombres):
            p, created = models.EstadoDeTarea.objects.get_or_create(nombre=nombre)
            log(p)

    def crear_estados_de_validaciones(self):
        nombres = [
            "Pendiente",
            "Objetada",
            "Aprobada"
            # "Pendiente", #1
            # "Revisión", #2
            # "Cerrado", #3,
            # "Eliminado", #4
            # "Conformacion", #5
            # "No valida" #6
        ]

        print("Creando Estados de Validaciones")
        bar = barra_de_progreso()

        for nombre in bar(nombres):
            p, created = models.EstadoDeValidacion.objects.get_or_create(nombre=nombre)
            log(p)

    def crear_prioridades_de_tareas(self):
        nombres = [
            "Alta",
            "Media",
            "Baja"
        ]

        print("Creando Prioridades de Tareas")
        bar = barra_de_progreso()

        for nombre in bar(nombres):
            p, created = models.PrioridadDeTarea.objects.get_or_create(nombre=nombre)
            log(p)

    def crear_niveles(self):
        nombres = ["Inicial", "Primaria", "Secundaria", "Superior"]

        print("Creando Niveles")
        bar = barra_de_progreso()

        for nombre in bar(nombres):
            p, created = models.Nivel.objects.get_or_create(nombre=nombre)
            log(p)

    def crear_tipos_de_gestion(self):
        nombres = ["Estatal", "Privada", "Compartida"]

        print("Creando Tipos de Gestión")
        bar = barra_de_progreso()

        for nombre in bar(nombres):
            p, created = models.TipoDeGestion.objects.get_or_create(nombre=nombre)
            log(p)

    def crear_areas(self):
        nombres = ["Urbana", "Rural"]

        print("Creando Areas")
        bar = barra_de_progreso()

        for nombre in bar(nombres):
            p, created = models.Area.objects.get_or_create(nombre=nombre)
            log(p)

    def crear_programas(self):
        nombres = [
            "Conectar Igualdad",
            "PAD",
            "Responsabilidad Empresarial",
            "Primaria Digital",
            "Escuelas del Futuro"
            ]

        print("Creando Programas")
        bar = barra_de_progreso()

        for nombre in bar(nombres):
            p, created = models.Programa.objects.get_or_create(nombre=nombre)
            log(p)

    def crear_experiencias(self):
        nombres = [
            "Técnico",
            "Pedagógico",
            "Administrativo",
            "Diseño",
            "Comunicación"
            ]

        print("Creando Experiencias")
        bar = barra_de_progreso()

        for nombre in bar(nombres):
            p, created = models.Experiencia.objects.get_or_create(nombre=nombre)
            log(p)

    def crear_contratos(self):
        nombres = [
            "PLANIED",
            "Planta/PLANIED",
            "Planta",
            "ConIg",
            "Ord. Tec."

            ]

        print("Creando Contactos")
        bar = barra_de_progreso()


        for nombre in bar(nombres):
            p, created = models.Contrato.objects.get_or_create(nombre=nombre)
            log(p)

    def crear_cargos(self):
        nombres = [
            ("FED", "Facilitador Educación Digital"),
            ("Coord", "Coordinador"),
            ("Adm", "Administrativo"),
            ("Coord EF", "Coordinador EF"),
            ("FED esp", "Facilitador Educación Digital Especial"),
            ("Coord Prov", "Coordinador Provincial")
            ]

        print("Creando Cargos")
        bar = barra_de_progreso()

        for nombre in bar(nombres):
            p, created = models.Cargo.objects.get_or_create(nombre=nombre[0], descripcion=nombre[1])
            log(p)

    def crear_cargos_escolares(self):
        nombres = [
            "Director",
            "Vice Director",
            "Secretario",
            "Maestro",
            "EMATP",
            "Prosecretario",
            "Preceptor",
            "Profesor",
            "Otro"
            ]

        print("Creando Cargos Escolares")
        bar = barra_de_progreso()

        for nombre in bar(nombres):
            p, created = models.CargoEscolar.objects.get_or_create(nombre=nombre)
            log(p)

    def crear_categorias_de_eventos(self):
        nombres = [
            "Acciones especiales/Congresos",
            "Acciones especiales/Desembarcos",
            "Acciones especiales/Encuentros masivos",
            "Acciones especiales/Prácticas profesionales",
            "Asistencia/Administrativa",
            "Asistencia/Pedagógica",
            "Asistencia/Técnica",
            "Escuelas del futuro/Seguimiento de actividades",
            "Escuelas del futuro/Seguimiento de acciones",
            "Capacitaciones/Sensibilización",
            "Capacitaciones/Docentes",
            "Capacitaciones/Alumnos",
            "Reunión/Online",
            "Reunión/Inspectores",
            "Reunión/Referente de área",
            "Reunión/Equipo",
            "Reunión/Planificación",
            "Reunión/Región Central",
            ]

        print("Creando Categorías de eventos")
        bar = barra_de_progreso()

        for nombre in bar(nombres):
            p, created = models.CategoriaDeEvento.objects.get_or_create(nombre=nombre)
            log(p)

    def limpiar_e_importar_permisos_con_grupos(self):
        # Elimina todos los permisos por omision de django.
        print("Borrando los permisos estándar de django")
        permisos_estandar = [x for x in Permission.objects.all() if x.name.startswith('Can ')]

        if permisos_estandar:
            print("Borrando %d" %(len(permisos_estandar)))
            [x.delete() for x in permisos_estandar]
        else:
            print("No hay permisos estandar para borrar")

        # Genera los permisos personalizados

        AGENDA_LISTAR = 'agenda.listar'
        AGENDA_CREAR = 'agenda.crear'

        ESCUELA_LISTAR = 'escuela.listar'
        ESCUELA_EDITAR = 'escuela.editar'
        ESCUELA_CONFORMAR = 'escuela.conformar'

        TAREA_LISTAR = 'tarea.listar'
        PAQUETES_LISTAR = 'paquetes.listar'
        VALIDACIONES_LISTAR = 'validaciones.listar'
        PERSONAS_LISTAR = 'personas.listar'

        permisos = [
            AGENDA_LISTAR, AGENDA_CREAR,
            ESCUELA_LISTAR, ESCUELA_EDITAR, ESCUELA_CONFORMAR,
            TAREA_LISTAR,
            PAQUETES_LISTAR,
            VALIDACIONES_LISTAR,
            PERSONAS_LISTAR,
        ]

        print("Actualizando el listado de permisos (creación o actualización)")
        bar = barra_de_progreso()

        for p in bar(permisos):
            modelo, permiso = p.split('.')

            tipo, _ = ContentType.objects.get_or_create(app_label='escuelas', model=modelo)
            Permission.objects.get_or_create(name=permiso, codename=p, content_type=tipo)



        grupos = {
            'Coordinador': [
                ESCUELA_LISTAR, ESCUELA_CONFORMAR, ESCUELA_EDITAR,
                AGENDA_LISTAR, AGENDA_CREAR,
            ],
            'Invitado': [
                ESCUELA_LISTAR,
                AGENDA_LISTAR,
            ],
            'Sin Definir': [
                ESCUELA_LISTAR,
                AGENDA_LISTAR,
            ],
            'Administrador': permisos, # LISTA con todos los permisos existentes
            'Facilitador': [
            ]
        }

        for nombre_de_grupo in grupos:

            (grupo, _) = Group.objects.get_or_create(name=nombre_de_grupo)

            for nombre_de_permiso in grupos[nombre_de_grupo]:
                permiso = Permission.objects.get(codename=nombre_de_permiso)
                grupo.permissions.add(permiso)


        print("Realizando asignación de grupos")

        asignaciones = [
            # ( Email laboral  ,  Nombre del grupo )
            ('ccane@abc.gob.ar', 'Administrador'),
            ('lvigolo@abc.gob.ar', 'Administrador'),
        ]

        for emailLaboral, grupo in asignaciones:
            perfil = models.Perfil.objects.get(emailLaboral=emailLaboral)
            perfil.definir_grupo_usando_nombre(grupo)
            perfil.save()


        print("Aplicando el grupo 'Sin definir' a todos los perfiles que no tengan grupo")
        bar = barra_de_progreso()

        for perfil in bar(models.Perfil.objects.all()):
            if not perfil.group:
                perfil.group = Group.objects.get(name='Sin Definir')
                perfil.save()
