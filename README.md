# SUITE 2 - API Backend



[![CircleCI](https://circleci.com/gh/Dte-ba/suite-backend.svg?style=svg)](https://circleci.com/gh/Dte-ba/suite-backend)

## ¿Cómo iniciar la aplicación?

El primer paso es crear un entorno virtual y activarlo :

```
virtualenv venv --no-site-packages
. venv/bin/activate
```

instalar las dependencias especificadas en el archivo
requirements.txt:

```
make iniciar
```

Luego, hay que preparar la base de datos de desarrollo:

```
make migrar
```

También es buena idea crear un usuario para poder
acceder al administrador de django:

```
make crear_usuario_admin
```

## Cómo iniciar el servidor

Para iniciar el servidor en modo desarrollo hay que
ejecutar el siguiente comando:

```
make serve
```

y luego abrir la dirección:

- http://127.0.0.1:8000/

o bien, la siguiente dirección para abrir la interfaz de administración:

- http://127.0.0.1:8000/admin



## Cómo crear un nuevo modelo de base de datos

Para crear un nuevo modelo en la base de datos hay que crear un nuevo
archivo dentro del directorio `suite/escuelas/models` y luego vincularlo desde
el archivo `suite/escuelas/models/__init__.py`.

Por ejemplo, vamos a suponer que queremos crear una tabla nueva que nos
permita guardar la dirección de un contacto asociado a una
escuela.

(Ojo, esto es un ejemplo ilustrativo, no contempla direcciones en
departamentos ni nada parecido, es solo un ejemplo rápido )

El modelo de datos actual es así:

![](imagenes/der_inicial.png)

Y lo que nos gustaría hacer es crear una tabla de domicilios que se vincule
con un contacto así:

![](imagenes/der_con_relacion.png)

Tendríamos que escribir un archivo nuevo llamado `suite/escuelas/models/domicilio.py`
con este contenido :

```
from django.db import models

class Domicilio(models.Model):
    calle = models.CharField(max_length=500)
    numeracion = models.IntegerField()

    class Meta:
        db_table = 'domicilios'
```

Y luego agregar esta linea al archivo `suite/escuelas/models/__init__.py`:

```
from domicilio import Domicilio
```

Y para que se relacione con un contacto tendríamos
que declarar la relación en la clase Contacto
(archivo `suite/escuelas/models/contacto.y`):

```
class Contacto(models.Model):
    # [Los otros campos irían acá]

    domicilio = models.ForeignKey('Domicilio', null=True)
```

Ahora, como cambiamos el modelo, necesitamos escribir una migración
para que django pueda modificar la estructura de la base de datos y migrar
todos los registros existentes.

Para crear una migración hay que escribir el comando:

```
make crear_migraciones
```

Lo que va a salir en pantalla es un reporte de los cambios que detectó
django y la ruta a un archivo conteniendo la migración:

```
Migrations for 'escuelas':
  suite/escuelas/migrations/0002_auto_20161203_2350.py:
    - Create model Domicilio
    - Add field domicilio to contacto
```

Lo interesante de este archivo, es que nos va a servir para hacer un seguimiento
de los cambios en la base de datos. Ese archivo se tiene que subir
al respositorio y le va a servir al equipo entero para replicar la mísma base
de datos en otra pc.

Por último, para que estos cambios impacten realmente en la base de datos
tenemos que ejecutar nuevamente:

```
make migrar
```

Por último, un paso opcional: si queremos investigar el SQL que django
generará para modificar la base de datos podemos usar el número de la
migración y lanzar un comando de consulta:

```
python suite/manage.py sqlmigrate escuelas 0002
```

Este comando va a imprimir (pero sin ejecutar) el código SQL que sugiere
la migración. Es importante notar que no es solo un "CREATE TABLE" y
"ALTER TABLE", Django se encarga de generar una tabla temporal con la
estructura vieja, crear una tabla nueva, mover los registros para no perder
ningún dato y dejar todo funcionando nuevamente.


### Cómo realizar las operaciones básicas del ORM

Para acceder al ORM y ejecutar algunas pruebas podemos usar el comando:

```
make shell
```

Esto abrirá un intérprete de python, con autocompletado y algunas utilidades
muy prácticas. Por ejemplo:

![](imagenes/shell.png)

Con `tab` podemos autocompletar, y usando el signo `?` o `??` a la derecha
de algún objeto podemos obtener ayuda sobre cómo utilizarlo:

![](imagenes/inspector.png)

Este intérprete de prueba también sirve para otras cosas, como para sacarnos
dudas a la hora de escribir un tests o investigar la API de django.

#### Cómo crear registros

Simplemente hay que crear un objeto desde la clase del modelo, cargar
valores y llamar a 'save':

```
>>> from escuelas import models
>>> domicilio = models.Domicilio()
>>> domicilio.calle = u"Saez Peña"
>>> domicilio.numeracion = 898
>>> domicilio.save()
>>> print(domicilio.id)
1
```

Obviamente para no rompera la encapsulación vamos a asegurarnos de
darle valores iniciales a los objetos cuando los creamos; esto es solo un ejemplo.

#### Cómo realizar listados y búsquedas

Para obtener el listado completo de registros para un
modelo podemos escribir algo así:

```
>>> models.Escuela.objects.all()
```

Para buscar por ID o nombre exacto así:

```
>>> models.Escuela.objects.filter(nombre="Sarmiento")
>>> models.Escuela.objects.filter(id=1)
```

Ver documentación completa en:

- https://docs.djangoproject.com/en/1.10/topics/db/queries/

#### Cómo borrar registros

Hay que conseguir una referencia al registro que se quiere borrar y luego
llamar al método `delete`:

```
>>> from escuelas import models
>>> d = models.Domicilio.objects.all()[0]
>>> d.delete()
(1, {u'escuelas.Contacto': 0, u'escuelas.Domicilio': 1})
```

### Cómo agregar un modelo al administrador

Para agregar un modelo al administrador hay que vincularlo
en el archivo `suite/escuelas/admin.py`.

Para seguir con nuestro ejemplo, debería quedar así:

```
from django.contrib import admin
import models

admin.site.register(models.Domicilio)
```

![](imagenes/admin_domicilio.png)



## API

La aplicación incluye una API para acceder a los modelos a traves del
estándar json-api. Para ver todas las rutas disponibles ingresá en:

- http://localhost:8000/api/

Si ves esa URL con un navegador, vas a poder pulsar en las URLs para
ingresar en cada recurso y navegar por cualquier link:

![](imagenes/api.png)

En cambio, si accedes a los datos desde CURL (o un frontend javascript) vas a ver
solamente los datos crudos:

```
> curl http://localhost:8000/api/
{"data":{"users":"http://localhost:8000/api/users/"}}
```

Para agregar algún modelo a esta API deberías crear
una vista y un serializador. Esto es bastante sencillo
de hacer, pero requiere seguir estos pasos y copiar/pegar un poco de código:

- Primero tendrías que crear la ruta en el archivo `suite/suite/urls.py`.

Por ejemplo, para exponer la API de los modelo Escuela
usamos esta linea:

```
router.register(r'escuelas', views.EscuelaViewSet)
```

- Luego tendrías que incluir una vista en el archivo
  `suite/escuelas/views.py`:

Volviendo al ejemplo del modelo Escuela, la vista quedaría
así:

```
class EscuelaViewSet(viewsets.ModelViewSet):
    queryset = Escuela.objects.all()
    serializer_class = serializers.EscuelaSerializer
```

Por último, hay que crear el serializador en el archivo
`suite/escuelas/serializers.py`, por ejemplo:


```
class EscuelaSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.Escuela
        fields = '__all__'
```

El campo `fields` sirve para indicar qué atributos se quieren exponer en
la api, no siempre se quieren mostrar todos los datos como acá. Mirá
la clase `UserSerializer` del mismo archivo para ver otro ejemplo de uso.

## Notas, consejos y trucos.


### Cómo salir del entorno virtual

Para salir del entorno se puede ejecutar el siguiente comando:

```
deactivate
```

### Cómo instalar dependencias


Si encontás alguna dependencia útil, podés
instalarla usando el comando `pip install`, por
ejemplo:


```
pip install rednose
```

Esto agregará la dependencia en el entorno virtual. Si querés
indicar en el repositorio que esta dependencia es obligatoria agregala
al archivo `requirements.txt` así:

```
pip freeze > requirements.txt
```

### Ocultar archivos .pyc en Atom

Python genera archivos .pyc para agilizar al conversión python -> bytecode,
pero esto ensucia un poco el treeview de un editor como atom:

![](imagenes/ocultar_pyc_1.png)

Atom reconoce que los archivos `.pyc` no son importantes (ya que están
en el archivo .gitignore) y por eso los muestra en color gris.


Para que estos archivos ni siquiera aparescan, se puede ingresar en las
prefenrencias del editor, luego en complemento treeview y activar la
opción para ocultar todos los archivos ignorados:

![](imagenes/ocultar_pyc_2.png)

Así debería quedar el treeview luego de guardar
los cambios:

![](imagenes/ocultar_pyc_3.png)


### Activar utf-8

Si ves un mensaje de la forma:

```
SyntaxError: Non-ASCII character '\xc3' in file ...
```


Simplemente agregá este comentario al principio del archivo que da errores:

```
# coding: utf-8
```


### Cómo generar un gráfico del modelo de datos

Primero tendrías que instalar graphviz en tu equipo, con
algún comando como este:

```
sudo apt-get install graphviz
```

Y luego ejecutar este comando:


```
make grafico
```

Se va a generar un archivo .png similar al siguiente:

![](imagenes/demo_grafico_db.png)

### Activar el autocompletado en Atom

Para activar el autocompletado desde el editor atom hay que instalar
un complemento llamado [autocomplete-python](https://atom.io/packages/autocomplete-python).

![](imagenes/autocompletado-1.png)

Una vez instalado, hay que ingresar en las preferencias del complemento
y colocar las rutas al binario de python (dentro del entorno virtual) y
también el directorio de bibliotecas dentro del entorno virtual:

- binarios: `/usr/bin/python;$PROJECT/venv/bin/python`
- bibliotecas: `$PROJECT/venv/lib/python2.7/site-packages`

![](imagenes/autocompletado-2.png)

Con esto listo, podríamos empezar a escribir código y ver cómo infiere
el autocompletado correctamente:

![](imagenes/autocompletado-3.png)

Nota: la primera vez que comenzamos a escribir, demora como 5 o 10 segundos
en aparecer la primer opción de autocompletado. Una vez que pasa esa primer
demora el resto de las sugerencias es inmediata.




## Deploy en producción

Primero hay que contar con un servidor que soporte dokku, hay una nota
que puede servirte de introducción a dokku aquí:

- http://blog.enjambrelab.com.ar/

También tendrías que tener instalada la extensión para usar bases de
dato postgres:

- https://github.com/dokku/dokku-postgres


En este punto, tu vps con dokku debería tener un dominio. 

Aquí usaremos el dominio dtelab.com.ar porque es el que estamos usando para desarrollo:

Para iniciar la instalación de la aplicación en dokku tenemos que escribir:


	git remote add desarrollo dokku@dtelab.com.ar:testing-suite-backend
	git push desarrollo master


La instancia de la aplicación quedará como un destino remoto de nuestro
repositorio, así que cada vez que busquemos hacer un deploy tenemos
que ejecutar el comando:

	git push desarrollo master


Donde "desarrollo" es el nombre que le damos a la instancia, que podría
ser cualquier otra cosa. Incluso podríamos tener una instancia "produccion",
"pruebas" etc...


	dokku postgres:create testing-suite-backend
	dokku postgres:info testing-suite-backend


Por último, hay que vincular la nueva base de datos con la aplicación:

	dokku postgres:link testing-suite-backend suite-backend-desarrollo

(el primer argumento de link es el nombre de la base de datos y el segundo
es el identificador de la aplicación).

Luego, desde la aplicación deberíamos conectarnos a la base de datos usando
la variable de entorno DATABASE_URL. Usando el comando `dokku config` se
puede consultar si esta variable se inicializó correctamente o no:

	> dokku config
	=====> suite-backend-desarrollo config vars
	DATABASE_URL:      postgres://postgres:612a369cxxxxx13@dokku-postgres-testing-suite-backend:5432/desarrollo_suite_backend
	DOKKU_APP_RESTORE: 1
	DOKKU_APP_TYPE:    herokuish
	DOKKU_NGINX_PORT:  80

Si no llega a estar correctamente configurado, hay que ejecutar el comando que
define la variable de entorno DATABASE_URL:

	dokku config:set DATABASE_URL=postgres://postgres:33bd2xxxxx@dokku-postgres-testing-suite-backend:5432/desarrollo_suite_backend

Por último, para ejecutar comandos sobre el entorno de desarrollo hay que
anteponer el prefijo `dokku run` y en algunos casos especificar el nombre
de la configuración del entorno:

	dokku run python manage.py migrate --settings=suite.desarrollo_settings
	dokku run python manage.py createsuperuser --settings=suite.desarrollo_settings


