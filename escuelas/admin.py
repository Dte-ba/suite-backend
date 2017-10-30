from django.contrib import admin
import models

admin.site.register(models.Contacto)

class EscuelaAdmin(admin.ModelAdmin):
    model = models.Escuela
    list_display = ('cue', 'nombre', 'localidad', 'nivel', 'modalidad', 'numero_de_region')
    search_fields = ('cue', 'nombre')

class PerfilAdmin(admin.ModelAdmin):
    model = models.Perfil
    list_display = ('user', 'nombre', 'apellido', 'group', 'region', 'dni', 'email')
    search_fields = ('nombre', 'apellido', 'dni')

class EventoAdmin(admin.ModelAdmin):
    model = models.Evento
    list_display = ('id', 'titulo', 'fecha', 'inicio', 'fecha_fin', 'fin',  'responsable')
    search_fields = ('id', 'titulo', 'legacy_id')

admin.site.register(models.Escuela, EscuelaAdmin)
admin.site.register(models.Evento, EventoAdmin)
admin.site.register(models.Perfil, PerfilAdmin)

admin.site.register(models.MotivoDeConformacion)

admin.site.register(models.TipoDeFinanciamiento)
admin.site.register(models.Nivel)
admin.site.register(models.Modalidad)
admin.site.register(models.TipoDeGestion)
admin.site.register(models.Area)
admin.site.register(models.Programa)

class LocalidadAdmin(admin.ModelAdmin):
    model = models.Localidad
    list_display = ('nombre', 'distrito')
    search_fields = ('id', 'nombre')

admin.site.register(models.Localidad, LocalidadAdmin)

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

admin.site.register(models.EstadoDeValidacion)

class ComentarioDeValidacionInline(admin.TabularInline):
    model = models.ComentarioDeValidacion

class ValidacionAdmin(admin.ModelAdmin):
    model = models.Validacion
    list_display = ('fecha_de_alta', 'fecha_de_modificacion', 'autor', 'cantidad_pedidas', 'cantidad_validadas', 'estado', 'observaciones', 'escuela')
    inlines = [
        ComentarioDeValidacionInline,
    ]

admin.site.register(models.Validacion, ValidacionAdmin)
admin.site.register(models.ComentarioDeValidacion)

class CategoriaDeEventoAdmin(admin.ModelAdmin):
    model = models.CategoriaDeEvento
    list_display = ('nombre', )

admin.site.register(models.CategoriaDeEvento, CategoriaDeEventoAdmin)

class PisoAdmin(admin.ModelAdmin):
    model = models.Piso
    list_display = ('servidor', 'serie', 'ups', 'rack', 'estado', 'llave')
    search_fields = ('id', 'servidor', 'serie', 'estado', 'llave')

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

class PaqueteAdmin(admin.ModelAdmin):
    model = models.Paquete
    list_display = (
        'legacy_id',
        'escuela',
        'fecha_pedido',
        'ne',
        'id_hardware',
        'marca_de_arranque',
        'comentario',
        'carpeta_paquete',
        'fecha_envio',
        'zip_paquete',
        'estado',
        'fecha_devolucion',
        'id_devolucion',
        'leido',
        'tpmdata'
    )
    search_fields = ('legacy_id', 'estado', 'escuela')

admin.site.register(models.Paquete, PaqueteAdmin)
