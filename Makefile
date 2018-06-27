VERSION=$(shell git describe --tags)
NOMBRE=suite

N=[0m
R=[00;31m
G=[01;32m
Y=[01;33m
B=[01;34m
L=[01;30m

BIN_MANAGE=python manage.py
BIN_MANAGE_RELATIVO=python manage.py
BIN_DOKKU=~/.dokku/contrib/dokku_client.sh
DB_NAME=suite-produccion
DB_NOMBRE_DEL_DUMP= ~/Dropbox/4cores/Backups/suite-backend-produccion-dtelab_`date +'%Y%m%d_%Hhs%Mmin'`.dump
DB_DUMP_MAS_RECIENTE=`ls -Art ~/Dropbox/4cores/Backups/*.dump  | tail -n 1`
DB_URL="postgres://postgres:postgress@localhost/suite"

comandos:
	@echo ""
	@echo "${B}Comandos disponibles para ${G}${NOMBRE}${N} (versión: ${VERSION})"
	@echo ""
	@echo "  ${Y}Para desarrolladores${N}"
	@echo ""
	@echo "    ${G}iniciar${N}                     Instala todas las dependencias."
	@echo "    ${G}crear_migraciones${N}           Genera las migraciones."
	@echo "    ${G}crear_usuario_admin${N}         Genera un usuario administrador."
	@echo "    ${G}cargar_datos${N}                Carga toda la información inicial de los datos (escuelas + usuarios + etc...)."
	@echo "    ${G}cargar_datos filtro='a'${N}     Permite lanzar la importación de un comando en particular."
	@echo "    ${G}cargar_datos depuracion='1'${N} Activa el modo verbose."
	@echo "    ${G}cargar_datos perfil_id='1'${N} Ejecuta los comandos solo para ese perfil_id."
	@echo "    ${G}cargar_usuarios_demo${N}        Carga usuarios de prueba."
	@echo "    ${G}reiniciar_contraseñas${N}       Le aplica la contraseña 'asdasd123' a todos los usuarios."
	@echo ""
	@echo "    ${G}generar_estaticos${N}   Genera los archivos estáticos."
	@echo "    ${G}migrar${N}              Ejecuta las migraciones sobre la base de datos."
	@echo "    ${G}test${N}                Ejecuta los tests."
	@echo "    ${G}test_continuos${N}      Ejecuta los tests en forma contínua."
	@echo "    ${G}ejecutar${N}            Ejecuta el servidor en modo desarrollo."
	@echo "    ${G}ejecutar_produccion${N} Ejecuta el servidor usando postgres."
	@echo "    ${G}ejecutar_worker${N}     Ejecuta el servidor para tareas con redis queue."
	@echo "    ${G}monitor${N}             Muestra los trabajos del worker."
	@echo "    ${G}version${N}             Ingrementa la versión y realiza un deploy en circle.ci"
	@echo ""
	@echo "  ${Y}Para gestionar datos${N}"
	@echo ""
	@echo "    $(G)generar_fixture_desde_base_de_datos$(N)   Genera un fixture nuevo."
	@echo "    $(G)realizar_backup_desde_produccion$(N)      Descarga y guardar un dump en dropbox."
	@echo "    $(G)cargar_ultimo_dump_localmente$(N)         Carga el último dump de dropbox sobre un postgres local."
	@echo "    $(G)limpiar_registros_duplicados$(N)          Detecta y elimina localidades y distritos duplicados."
	@echo ""
	@echo ""


iniciar:
	@pipenv install

migrar:
	@pipenv run ${BIN_MANAGE} migrate --noinput

test: migrar
	@clear;
	@echo "${G}Ejecutando tests ...${N}"
	dropdb --if-exists suite-test -e; createdb suite-test
	@pipenv run "${BIN_MANAGE_RELATIVO} test" # -v 2"


test_continuos: test_live

test_live:
	@make test; watchmedo shell-command --patterns="*.py" --recursive --command='make test' .

ejecutar:
	@pipenv run ${BIN_MANAGE_RELATIVO} runserver

ejecutar_produccion: migrar ejecutar

ejecutar_worker:
	@pipenv run python manage.py rqworker default

monitor:
	@pipenv run python manage.py rqstats --interval=1

shell:
	@pipenv run ${BIN_MANAGE} shell

crear_migraciones:
	@pipenv run ${BIN_MANAGE} makemigrations

crear_usuario_admin:
	@pipenv run ${BIN_MANAGE} createsuperuser

generar_fixture_desde_base_de_datos:
	@echo ""
	@echo "$(V)Generando fixture y guardándolo en el archivo fixture_db.json$(N)"
	@echo ""
	python manage.py dumpdata --indent 2 --natural-foreign --natural-primary -o fixture_db.json

generar_estaticos:
	python manage.py collectstatic

filtro=""
depuracion="0"

cargar_datos:
	@pipenv run python manage.py cargar_datos --filtro $(filtro) --depuracion $(depuracion) --perfil_id $(perfil_id)

cargar_usuarios_demo:
	@pipenv run python scripts/cargar_usuarios_demo.py

limpiar_registros_duplicados:
	@pipenv run python scripts/limpiar_registros_duplicados.py

realizar_backup_desde_produccion:
	@echo "${G}Creando el archivo ${DB_NOMBRE_DEL_DUMP}${N}"
	${BIN_DOKKU} postgres:export ${DB_NAME} > ${DB_NOMBRE_DEL_DUMP}

reiniciar_contraseñas:
	@pipenv run python scripts/reiniciar_contraseñas.py

cargar_ultimo_dump_localmente:
	@echo "${G}Se cargará el dump mas reciente: ${DB_DUMP_MAS_RECIENTE}${N}"
	dropdb --if-exists suite -e; createdb suite
	pg_restore --no-acl --no-owner -d suite ${DB_DUMP_MAS_RECIENTE}

version:
	pipenv run bumpversion patch --verbose
	git push
	git push --tags
