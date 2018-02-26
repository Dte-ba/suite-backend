from rq import get_current_job
from escuelas import models

def crear_modelo_trabajo(nombre):
    job_id = ""
    job = get_current_job()

    if job:
        job_id = job.id

    return models.Trabajo.objects.create(nombre=nombre, trabajo_id=job_id)
