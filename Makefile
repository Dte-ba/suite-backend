NOMBRE=suite

N=[0m
R=[00;31m
G=[01;32m
Y=[01;33m
B=[01;34m
L=[01;30m

BIN_MANAGE=python suite/manage.py
BIN_MANAGE_RELATIVO=cd suite; python manage.py
BIN_ESTA_DENTRO_DE_VENV=python utils/esta_dentro_de_entorno_virtual.py

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
	@echo "    ${G}test${N}                Ejecuta los tests."
	@echo "    ${G}test_live${N}           Ejecuta los tests en forma contínua."
	@echo "    ${G}serve${N}               Ejecuta el servidor en modo desarrollo."
	@echo "    ${G}lint${N}                Busca errores o inconsistencias en el código."
	@echo "    ${G}ayuda${N}               Muestra una listado de todos los comandos django."
	@echo ""
	@echo ""


dependencias: esta_dentro_de_un_entorno_virtual
	@echo "${G}actualizando dependencias pip ...${N}"
	@pip install -r requirements.txt | sed '/Requirement\ \w*/d'

esta_dentro_de_un_entorno_virtual:
	@${BIN_ESTA_DENTRO_DE_VENV}

iniciar: dependencias

migrar: dependencias
	${BIN_MANAGE} migrate

test: dependencias
	@clear;
	@echo "${G}Ejecutando tests ...${N}"
	@${BIN_MANAGE_RELATIVO} test

test_live: dependencias
	@make test; watchmedo shell-command --patterns="*.py" --recursive --command='make test' .


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
	pyflakes suite
