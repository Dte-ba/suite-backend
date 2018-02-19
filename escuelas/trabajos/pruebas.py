from django_rq import job
import time
import utils

@job
def sumar(a, b):
    trabajo = utils.crear_modelo_trabajo("sumar a+b")

    for x in range(10):
        estado = "trabajando %d/10 ..." %(x)
        #print(estado)
        trabajo.actualizar_paso(x, 10, estado)
        time.sleep(1)

    resultado = a + b
    trabajo.resultado = str(resultado)
    trabajo.save()

    return resultado
