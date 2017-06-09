from django.contrib import admin
import models

admin.site.register(models.Contacto)
admin.site.register(models.Escuela)
admin.site.register(models.Evento)
admin.site.register(models.Perfil)

admin.site.register(models.TipoDeFinanciamiento)
admin.site.register(models.Nivel)
admin.site.register(models.TipoDeGestion)
admin.site.register(models.Area)
admin.site.register(models.Programa)

class MunicipioInline(admin.TabularInline):
    model = models.Municipio

class RegionAdmin(admin.ModelAdmin):
    ordering = ("numero", )
    inlines = [
        MunicipioInline,
    ]

admin.site.register(models.Region, RegionAdmin)
