# coding: utf-8
import sendgrid
from sendgrid.helpers.mail import *
from suite import settings

def enviar_correo(desde, hasta, asunto, mensaje):
    api = settings.SENDGRID_API_KEY

    if not api:
        raise Exception(u"Falta especificar SENDGRID_API_KEY en la configuración")

    sg = sendgrid.SendGridAPIClient(apikey=api)
    from_email = Email(desde)
    to_email = Email(hasta)
    subject = asunto
    content = Content("text/html", mensaje)
    mail = Mail(from_email, asunto, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())

    return [
        response.status_code,
        response.body,
        response.headers,
    ]
