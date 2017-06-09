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
admin.site.register(models.Localidad)

class DistritoInline(admin.TabularInline):
    model = models.Distrito

class RegionAdmin(admin.ModelAdmin):
    inlines = [
        DistritoInline,
    ]

class LocalidadInline(admin.TabularInline):
    model = models.Localidad

class DistritoAdmin(admin.ModelAdmin):
    inlines = [
        LocalidadInline,
    ]

admin.site.register(models.Region, RegionAdmin)
admin.site.register(models.Distrito, DistritoAdmin)
