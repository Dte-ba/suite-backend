# evaluacion-django-suite

[![Build Status](https://travis-ci.org/hugoruscitti/evaluacion-django-suite.svg?branch=master)](https://travis-ci.org/hugoruscitti/evaluacion-django-suite)

## ¿Cómo iniciar la aplicación?

El primer paso es crear un entorno virtual y activarlo:

```
virtualenv venv
. venv/bin/activate
```

Luego, hay que preparar la base de datos de desarrollo:

```
python project/manage.py migrate
```

También es buena idea crear un usuario para poder
acceder al administrador de django:

```
python project/manage.py createsuperuser
```

## Cómo iniciar el servidor

Para iniciar el servidor en modo desarrollo hay que
ejecutar el siguiente comando:

```
python project/manage.py runserver
```

y luego abrir la dirección:

- http://127.0.0.1:8000/

o bien, la siguiente dirección para abrir la interfaz de administración:

- http://127.0.0.1:8000/admin
