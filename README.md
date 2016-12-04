# evaluacion-django-suite

[![Build Status](https://travis-ci.org/hugoruscitti/evaluacion-django-suite.svg?branch=master)](https://travis-ci.org/hugoruscitti/evaluacion-django-suite)

## ¿Cómo iniciar la aplicación?

El primer paso es crear un entorno virtual y activarlo:

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
make admin
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

Para crear un nuevo modelo en la base de datos hay que crear una nueva clase dentro del archivo `suite/escuelas/models.py`.

Por ejemplo, vamos a suponer que queremos crear una nueva tabla en nuestro
modelo que nos permita guardar la dirección de un contacto asociado a una
escuela.

(Ojo, esto es un ejemplo ilustrativo, no contempla direcciones en
departamentos ni nada parecido, es solo un ejemplo rápido)

El modelo actual es así:

![](imagenes/der_inicial.png)

Y lo que nos gustaría hacer es crear una tabla de domicilios que se vincule
con un contacto:

![](imagenes/der_con_relacion.png)

Tendríamos que escribir dentro de `suite/escuelas/models.py` así:

```
class Domicilio(models.Model):
    calle = models.CharField(max_length=500)
    numeracion = models.IntegerField()

    class Meta:
        db_table = 'domicilios'
```

Y para que se relacione con un contacto tendríamos
que declarar la relación en la clase Contacto:

```
class Contacto(models.Model):
    # [Los otros campos irían acá]

    domicilio = models.ForeignKey('Domicilio', null=True)
```

Ahora, como cambiamos el modelo, necesitamos escribir una migración
para que django pueda modificar la estructura de la base de datos y migrar
los datos existentes.

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

Lo interesante de este archivo, es que nos servirá para hacer un seguimiento
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
