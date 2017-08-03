from django.contrib import admin
import models

admin.site.register(models.Contacto)

class EscuelaAdmin(admin.ModelAdmin):
    model = models.Escuela
    list_display = ('cue', 'nombre', 'localidad')
    search_fields = ('cue', 'nombre')

class PerfilAdmin(admin.ModelAdmin):
    model = models.Perfil
    list_display = ('user', 'nombre', 'apellido', 'grupo', 'dni', 'email')
    search_fields = ('user', 'nombre', 'apelido', 'dni')

class EventoAdmin(admin.ModelAdmin):
    model = models.Evento
    list_display = ('titulo', 'fecha', 'inicio', 'fin', 'todoElDia', 'responsable')

admin.site.register(models.Escuela, EscuelaAdmin)
admin.site.register(models.Evento, EventoAdmin)
admin.site.register(models.Perfil, PerfilAdmin)

admin.site.register(models.TipoDeFinanciamiento)
admin.site.register(models.Nivel)
admin.site.register(models.TipoDeGestion)
admin.site.register(models.Area)
admin.site.register(models.Programa)
admin.site.register(models.Localidad)

admin.site.register(models.Experiencia)
admin.site.register(models.Cargo)
admin.site.register(models.Contrato)

class ComentarioDeTareaInline(admin.TabularInline):
    model = models.ComentarioDeTarea

class TareaAdmin(admin.ModelAdmin):
    inlines = [
        ComentarioDeTareaInline,
    ]

admin.site.register(models.Tarea, TareaAdmin)
admin.site.register(models.MotivoDeTarea)
admin.site.register(models.PrioridadDeTarea)
admin.site.register(models.EstadoDeTarea)
admin.site.register(models.ComentarioDeTarea)

class CategoriaDeEventoAdmin(admin.ModelAdmin):
    model = models.CategoriaDeEvento
    list_display = ('nombre', )

admin.site.register(models.CategoriaDeEvento, CategoriaDeEventoAdmin)

class PisoAdmin(admin.ModelAdmin):
    model = models.Piso
    list_display = ('servidor', 'serie', 'ups', 'rack', 'estado', 'llave')

admin.site.register(models.Piso, PisoAdmin)


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
