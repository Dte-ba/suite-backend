# coding: utf-8
from django.db import models

class Region(models.Model):
    numero = models.CharField(max_length=10)
    
    def __unicode__(self):
        return u"Región %s" %(self.numero)

    class Meta:
        db_table = 'regiones'
        verbose_name_plural = "regiones"
