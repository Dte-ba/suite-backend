# coding: utf-8
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Perfil(models.Model):
    nombre = models.CharField(max_length=200, default="")
    apellido = models.CharField(max_length=200, default="")
    dni = models.CharField(max_length=200, default="0000")
    cuit = models.CharField(max_length=200, default="0000")
    fechadenacimiento = models.DateField(default="2010-10-10")
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=1)

    def __unicode__(self):
        return self.dni

    class Meta:
        db_table = 'perfiles'
        verbose_name_plural = "perfiles"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.perfil.save()
