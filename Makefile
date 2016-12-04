NOMBRE=suite

N=[0m
G=[01;32m
Y=[01;33m
B=[01;34m
L=[01;30m

BIN_MANAGE=python suite/manage.py

comandos:
	@echo ""
	@echo "${B}Comandos disponibles para ${G}${NOMBRE}${N}"
	@echo ""
	@echo "  ${Y}Para desarrolladores${N}"
	@echo ""
	@echo "    ${G}iniciar${N}             Instala todas las dependencias."
	@echo "    ${G}crear_migraciones${N}   Genera las migraciones."
	@echo "    ${G}migrar${N}              Ejecuta las migraciones sobre la base de datos."
	@echo "    ${G}admin${N}               Genera el usuario root para la sección ADMIN."
	@echo "    ${G}test${N}                Ejecuta los tests."
	@echo "    ${G}serve${N}               Ejecuta el servidor en modo desarrollo."
	@echo "    ${G}ayuda${N}               Muestra una listado de todos los comandos django."
	@echo ""
	@echo ""


iniciar:
	@echo "${G}instalando dependencias ...${N}"
	@pip install -r requirements.txt

migrar:
	${BIN_MANAGE} migrate

test:
	${BIN_MANAGE} test

serve:
	${BIN_MANAGE} runserver

s: serve
server: serve

ayuda:
	${BIN_MANAGE}

shell:
	${BIN_MANAGE} shell

crear_migraciones:
	${BIN_MANAGE} makemigrations

admin:
  ${BIN_MANAGE} createsuperuser
