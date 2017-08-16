# coding: utf-8
from __future__ import unicode_literals
import sys
import pprint
import os
import django
import pprint
from openpyxl import load_workbook

sys.path.append("..")
sys.path.append(".")

def log(mensaje, nivel=0):
    print("  " * nivel + " - " + mensaje)

if len(sys.argv) < 2:
    print("Numero de parámetros incorrectos")
    sys.exit(status=1)


# Configuración inicial de django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "suite.settings")
django.setup()

from escuelas import models
from django.contrib.auth.models import User

ARCHIVO = sys.argv[1]
LIMITE_DE_FILAS = 300

log("iniciando la importación del archivo: " + ARCHIVO)
wb = load_workbook(ARCHIVO)

columnas_como_string = ", ".join(wb.get_sheet_names())
log("Las páginas de la planilla son:", nivel=1)
log(columnas_como_string, nivel=2)

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

for indice, fila in enumerate(wb.active.rows):

    if indice is 0:
        continue;             # Ignora la cabecera

    if not fila[1].value:
        log("Terminando en la fila %d porque no parece haber mas registros." %(indice + 1), nivel=0)
        break

    log(u"Procesando fila '%d'" %(indice +1), nivel=0)

    try:
        valores = obtener_valores_desde_fila(fila)

        if valores['fechaDeRenuncia']:
            log(u"Renunció")
            fechaDeRenuncia=formatear_fecha(valores['fechaDeRenuncia'])
        else:
            log(u"Perfil activo")
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
            log(u"No tiene expediente")
            expediente=valores['expediente']
        else:
            expediente="Sin Datos"

        if valores['titulo']:
            titulo=valores['titulo']
        else:
            log(u"No tiene título")
            titulo="Sin Datos"

        fechaDeIngreso=formatear_fecha(valores['fechaDeIngreso'])

        if valores['perfil']:
            experiencia=valores['perfil']
        else:
            log(u"No tiene perfil")
            experiencia="Sin Datos"

        dni=str(valores['dni'])

        if valores['cuil']:
            cuil=str(valores['cuil'])
        else:
            log(u"No tiene CUIL")
            cuil="Sin Datos"

        if valores['cbu']:
            cbu=valores['cbu']
        else:
            log(u"No tiene cbu")
            cbu="Sin Datos"

        if valores['email']:
            email=valores['email']
        else:
            log(u"No tiene email")
            email="Sin Datos"

        if valores['email_laboral']:
            email_laboral=valores['email_laboral']
        else:
            log(u"No tiene email laboral")
            email_laboral=apellido+"@abc.gob.ar"

        email_laboral = email_laboral.lower()

        if valores['direccion']:
            direccion=valores['direccion']
        else:
            log(u"No tiene direccion")
            direccion="Sin Datos"

        localidad=valores['localidad'].title()
        codigo_postal=str(valores['codigo_postal'])

        if valores['fechaDeNacimiento']:
            fechaDeNacimiento=formatear_fecha(valores['fechaDeNacimiento'])
        else:
            log(u"No tiene fecha de nacimiento")
            fechaDeNacimiento=None

        if valores['telefono_celular']:
            telefono_celular=valores['telefono_celular']
        else:
            log(u"No tiene telefono celular")
            telefono_celular="Sin Datos"

        if valores['telefono_particular']:
            log(u"No tiene telefono Particular")
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
        print("-----")
        log(u"Fila %d - ****** OMITIDA, TypeError. La fila contiene caracteres incorrectos." %(indice + 1), nivel=0)
        filas_omitidas_o_con_errores += 1
        filas_omitidas_lista += ", " + str(indice + 1)
        print(e)
        print("-----")
        continue


    # try:
    #     valores = obtener_valores_desde_fila(fila)
    # except AttributeError:
    #     log(u"Fila %d - ****** OMITIDA, la fila contiene caracteres incorrectos." %(indice + 1), nivel=0)
    #     continue

    log(u"Fila %d - Cargando datos de perfil para consultor: '%s'" %(indice + 1, valores["consultor"]), nivel=0)
    print("")
    print("Apellido: " + apellido)
    print("Nombres: " + nombre)
    print("Region: " + region)
    print("Cargo: " + cargo)
    print("Contrato: " + contrato)
    print("Carga horaria: " + carga_horaria)
    print("Expediente: " + expediente)
    #print("Fecha de Ingreso: " + fechaDeIngreso)
    # print("Fecha de Renuncia: " + fechaDeRenuncia)
    print("Titulo: " + titulo)
    print("Perfil: " + experiencia)
    print("DNI: " + dni)
    print("CUIL: " + cuil)
    print("CBU: " + cbu)
    print("Email: " + email)
    print("Email Laboral: " + email_laboral)
    print("Direccion: " + direccion)
    print("Localidad: " + localidad)
    print("Codigo Postal: " + codigo_postal)
    #print("Fecha de nacimiento: " + fechaDeNacimiento)
    print("Telefono Celular: " + telefono_celular)
    print("Telefono Particular: " + telefono_particular)
    print("Username: " + username)
    print("Password: " + default_pass)
    print("-----")
    print("")

    filas_procesadas += 1

    if indice > LIMITE_DE_FILAS:
        break


log("Terminó la ejecución")

print("")
print("Resumen:")
print("")
print(" - cantidad total de filas:                       " + str(indice - 1))
print(" - filas procesadas:                              " + str(filas_procesadas))
print(" - cantidad de filas que fallaron:                " + str(indice - 1 - filas_procesadas))

print(" - filas que fallaron:                            " + str(filas_omitidas_lista))
# print(" - filas con error u omitidas:                    " + str(filas_omitidas_o_con_errores))
# print(" - cantidad de socios sin grupo familiar:         " + str(cantidad_de_socios_sin_grupo_familiar))
# print(" - cantidad de perfiles que renunciaron: " + str(cantidad_de_perfiles_con_renuncia))
print("")
print("")
