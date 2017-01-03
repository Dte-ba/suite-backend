NOMBRE=suite

N=[0m
R=[00;31m
G=[01;32m
Y=[01;33m
B=[01;34m
L=[01;30m

BIN_MANAGE=python manage.py
BIN_MANAGE_RELATIVO=python manage.py

comandos:
	@echo ""
	@echo "${B}Comandos disponibles para ${G}${NOMBRE}${N}"
	@echo ""
	@echo "  ${Y}Para desarrolladores${N}"
	@echo ""
	@echo "    ${G}iniciar${N}             Instala todas las dependencias."
	@echo "    ${G}crear_migraciones${N}   Genera las migraciones."
	@echo "    ${G}crear_usuario_admin${N} Genera un usuario administrador."
	@echo "    ${G}migrar${N}              Ejecuta las migraciones sobre la base de datos."
	@echo "    ${G}grafico${N}             Genera un grafico del modelo de datos en .PNG"
	@echo "    ${G}test${N}                Ejecuta los tests."
	@echo "    ${G}test_continuos${N}      Ejecuta los tests en forma contínua."
	@echo "    ${G}ejecutar${N}            Ejecuta el servidor en modo desarrollo."
	@echo "    ${G}lint${N}                Busca errores o inconsistencias en el código."
	@echo "    ${G}ayuda${N}               Muestra una listado de todos los comandos django."
	@echo ""
	@echo ""


dependencias: _esta_dentro_de_un_entorno_virtual
	@echo "${G}actualizando dependencias pip ...${N}"
	@pip install -r requirements.txt | sed '/Requirement\ \w*/d'

_esta_dentro_de_un_entorno_virtual:
	@python utils/esta_dentro_de_entorno_virtual.py

iniciar: dependencias

migrar: dependencias
	${BIN_MANAGE} migrate

test: dependencias
	@clear;
	@echo "${G}Ejecutando tests ...${N}"
	@make lint
	@${BIN_MANAGE_RELATIVO} test


test_continuos: test_live

test_live: dependencias
	@make test; watchmedo shell-command --patterns="*.py" --recursive --command='make test' .

ejecutar: serve

serve: dependencias
	${BIN_MANAGE} runserver

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

lint:
	@pyflakes escuelas

_esta_instalado_graphviz:
	@python utils/esta_instalado_graphviz.py
	
grafico: _esta_instalado_graphviz
	@echo "Graficando modelo de base de datos ..."
	@${BIN_MANAGE} graph_models escuelas --no-color -g -o grafico_db.png
	@echo "Se ha creado el archivo grafico_db.png"
