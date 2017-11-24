from django.contrib import admin
import models
from django.contrib.auth.models import Permission
from dal import autocomplete
from django import forms

class CustomModelAdmin(admin.ModelAdmin):

    class Media:
         js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            )

class EscuelaForm(forms.ModelForm):

    class Meta:
        model = models.Escuela
        fields = ('__all__')
        widgets = {
            'localidad': autocomplete.ModelSelect2()
        }

class EscuelaAdmin(CustomModelAdmin):
    form = EscuelaForm
    model = models.Escuela
    list_display = ('id', 'cue', 'nombre', 'localidad', 'nivel', 'modalidad', 'numero_de_region')
    search_fields = ('cue', 'nombre')

class PerfilForm(forms.ModelForm):

    class Meta:
        model = models.Perfil
        fields = ('__all__')
        widgets = {
            'localidad': autocomplete.ModelSelect2(),
            'user': autocomplete.ModelSelect2()
        }

class PerfilAdmin(CustomModelAdmin):
    form = PerfilForm
    model = models.Perfil
    list_display = ('user', 'nombre', 'apellido', 'group', 'region', 'dni', 'email')
    search_fields = ('nombre', 'apellido', 'dni')

class EventoAdmin(CustomModelAdmin):
    model = models.Evento
    list_display = ('id', 'titulo', 'fecha', 'inicio', 'fecha_fin', 'fin',  'responsable')
    search_fields = ('id', 'titulo', 'legacy_id')



class LocalidadForm(forms.ModelForm):

    class Meta:
        model = models.Localidad
        fields = ('__all__')
        widgets = {
            'distrito': autocomplete.ModelSelect2()
        }

class LocalidadAdmin(CustomModelAdmin):
    form = LocalidadForm
    model = models.Localidad
    list_display = ('id', 'nombre', 'distrito', 'cantidad_de_escuelas', 'numero_de_region', 'cantidad_de_perfiles_con_domicilio_vinculado')
    search_fields = ('id', 'nombre',)


class ComentarioDeTareaInline(admin.TabularInline):
    model = models.ComentarioDeTarea

class TareaAdmin(admin.ModelAdmin):
    inlines = [
        ComentarioDeTareaInline,
    ]


class ComentarioDeValidacionInline(admin.TabularInline):
    model = models.ComentarioDeValidacion

class ValidacionAdmin(admin.ModelAdmin):
    model = models.Validacion
    list_display = ('fecha_de_alta', 'fecha_de_modificacion', 'autor', 'cantidad_pedidas', 'cantidad_validadas', 'estado', 'observaciones', 'escuela')
    inlines = [
        ComentarioDeValidacionInline,
    ]


class CategoriaDeEventoAdmin(CustomModelAdmin):
    model = models.CategoriaDeEvento
    list_display = ('nombre', )


class PisoAdmin(CustomModelAdmin):
    model = models.Piso
    list_display = ('servidor', 'serie', 'ups', 'rack', 'estado', 'llave')
    search_fields = ('id', 'servidor', 'serie', 'estado', 'llave')



class DistritoInline(admin.TabularInline):
    model = models.Distrito

class RegionAdmin(CustomModelAdmin):
    inlines = [
        DistritoInline,
    ]

class LocalidadInline(admin.TabularInline):
    model = models.Localidad

class DistritoAdmin(CustomModelAdmin):
    inlines = [
        LocalidadInline,
    ]
    list_display = ('id', 'nombre', 'cantidad_de_localidades', 'cantidad_de_escuelas', 'region', 'cantidad_de_perfiles_en_la_region')
    search_fields = ('id', 'nombre')

class PaqueteAdmin(CustomModelAdmin):
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

admin.site.register(Permission)
admin.site.register(models.Contacto)
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
admin.site.register(models.Localidad, LocalidadAdmin)

admin.site.register(models.Experiencia)
admin.site.register(models.Cargo)
admin.site.register(models.Contrato)

admin.site.register(models.Tarea, TareaAdmin)
admin.site.register(models.MotivoDeTarea)
admin.site.register(models.PrioridadDeTarea)
admin.site.register(models.EstadoDeTarea)
admin.site.register(models.ComentarioDeTarea)

admin.site.register(models.EstadoDeValidacion)
admin.site.register(models.Validacion, ValidacionAdmin)
admin.site.register(models.ComentarioDeValidacion)
admin.site.register(models.CategoriaDeEvento, CategoriaDeEventoAdmin)
admin.site.register(models.Piso, PisoAdmin)
admin.site.register(models.Region, RegionAdmin)
admin.site.register(models.Distrito, DistritoAdmin)
admin.site.register(models.Paquete, PaqueteAdmin)
