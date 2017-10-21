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
DB_NOMBRE_DEL_DUMP= ~/Dropbox/4cores/Backups/suite-backend-produccion-dtelab_`date +'%Y%m%d'`.dump
DB_DUMP_MAS_RECIENTE=~/Dropbox/4cores/Backups/`ls -Art ~/Dropbox/4cores/Backups/  | tail -n 1`

comandos:
	@echo ""
	@echo "${B}Comandos disponibles para ${G}${NOMBRE}${N}"
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
	@echo ""
	@echo "    ${G}generar_estaticos${N}   Genera los archivos estáticos."
	@echo "    ${G}migrar${N}              Ejecuta las migraciones sobre la base de datos."
	@echo "    ${G}grafico${N}             Genera un grafico del modelo de datos en .PNG"
	@echo "    ${G}test${N}                Ejecuta los tests."
	@echo "    ${G}test_continuos${N}      Ejecuta los tests en forma contínua."
	@echo "    ${G}ejecutar${N}            Ejecuta el servidor en modo desarrollo."
	@echo "    ${G}ayuda${N}               Muestra una listado de todos los comandos django."
	@echo ""
	@echo "  ${Y}Para gestionar datos${N}"
	@echo ""
	@echo "    $(G)generar_fixture_desde_base_de_datos$(N)   Genera un fixture nuevo."
	@echo "    $(G)realizar_backup_desde_produccion$(N)      Descarga y guardar un dump en dropbox."
	@echo "    $(G)cargar_ultimo_dump_localmente$(N)         Carga el último dump de dropbox sobre un postgres local."
	@echo ""
	@echo ""


dependencias: #_esta_dentro_de_un_entorno_virtual
	@echo "${G}actualizando dependencias pip ...${N}"
	@pip install -r requirements.txt | sed '/Requirement\ \w*/d'

#_esta_dentro_de_un_entorno_virtual:
#	@python utils/esta_dentro_de_entorno_virtual.py

iniciar: dependencias

migrar: dependencias
	${BIN_MANAGE} migrate --noinput

test: dependencias
	@clear;
	@echo "${G}Ejecutando tests ...${N}"
	@${BIN_MANAGE_RELATIVO} test


test_continuos: test_live

test_live: dependencias
	@make test; watchmedo shell-command --patterns="*.py" --recursive --command='make test' .

ejecutar: migrar serve

serve: dependencias
	${BIN_MANAGE} runserver
	#${BIN_MANAGE} testserver escuelas/fixtures/*

s: serve
server: serve

ayuda:
	${BIN_MANAGE}

shell: dependencias
	${BIN_MANAGE} shell

crear_migraciones:
	${BIN_MANAGE} makemigrations

crear_usuario_admin:
	${BIN_MANAGE} createsuperuser

_esta_instalado_graphviz:
	@python utils/esta_instalado_graphviz.py

grafico: _esta_instalado_graphviz
	@echo "Graficando modelo de base de datos ..."
	@${BIN_MANAGE} graph_models escuelas --no-color -g -o grafico_db.png
	@echo "Se ha creado el archivo grafico_db.png"

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
	python manage.py cargar_datos --filtro $(filtro) --depuracion $(depuracion) --perfil_id $(perfil_id)

cargar_usuarios_demo:
	python scripts/cargar_usuarios_demo.py

realizar_backup_desde_produccion:
	@echo "${G}Creando el archivo ${DB_NOMBRE_DEL_DUMP}${N}"
	${BIN_DOKKU} postgres:export suite-backend-produccion-dtelab > ${DB_NOMBRE_DEL_DUMP}


cargar_ultimo_dump_localmente:
	@echo "${G}Se cargará el dump mas reciente: ${DB_DUMP_MAS_RECIENTE}${N}"
	dropdb --if-exists suite -e; createdb suite
	pg_restore --no-acl --no-owner -d suite ${DB_DUMP_MAS_RECIENTE}
