from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.static import static
from rest_framework.authtoken.views import obtain_auth_token


from easy_pdf.views import PDFTemplateView

import escuelas.views.escuela
import escuelas.views.user
from escuelas import views
from rest_framework import routers

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'users', escuelas.views.user.UserViewSet)
router.register(r'escuelas', escuelas.views.escuela.EscuelaViewSet)
router.register(r'contactos', views.ContactoViewSet)
router.register(r'eventos', views.EventoViewSet)
router.register(r'regiones', views.RegionViewSet)
router.register(r'perfiles', views.PerfilViewSet)
router.register(r'distritos', views.DistritoViewSet)
router.register(r'localidades', views.LocalidadViewSet)
router.register(r'programas', views.ProgramaViewSet)
router.register(r'tipos-de-financiamiento', views.TipoDeFinanciamientoViewSet)
router.register(r'tipos-de-gestion', views.TipoDeGestionViewSet)
router.register(r'areas', views.AreaViewSet)
router.register(r'niveles', views.NivelViewSet)
router.register(r'modalidades', views.ModalidadViewSet)
router.register(r'experiencias', views.ExperienciaViewSet)
router.register(r'cargos', views.CargoViewSet)
router.register(r'contratos', views.ContratoViewSet)
router.register(r'pisos', views.PisoViewSet)
router.register(r'cargos-escolares', views.CargoEscolarViewSet)
router.register(r'comentario-de-tareas', views.ComentarioDeTareaViewSet)
router.register(r'motivo-de-tareas', views.MotivoDeTareaViewSet)
router.register(r'motivos-de-conformacion', views.MotivoDeConformacionViewSet)
router.register(r'estado-de-tareas', views.EstadoDeTareaViewSet)
router.register(r'prioridad-de-tareas', views.PrioridadDeTareaViewSet)
router.register(r'tareas', views.TareaViewSet)
router.register('categorias-de-eventos', views.CategoriaDeEventoViewSet)
router.register('comentarios-de-validacion', views.ComentarioDeValidacionViewSet)
router.register('validaciones', views.ValidacionViewSet)
router.register('estados-de-validacion', views.EstadoDeValidacionViewSet)
router.register('estados-de-paquete', views.EstadoDePaqueteViewSet)
router.register('paquetes', views.PaqueteViewSet)
router.register('permissions', views.PermissionViewSet)
router.register('groups', views.GroupViewSet)
router.register('informes', views.informes.InformesViewSet, 'Informes')
router.register('trabajos', views.trabajos.TrabajosViewSet, 'Trabajos')
router.register('distribucion-de-paquetes', views.DistribucionDePaquetesViewSet, 'DistribucionDePaquetes')


router.register('mi-perfil', views.MiPerfilViewSet, 'Perfil')

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^demo/$', views.DemoPDFView.as_view(), name="demo"),
    url(r'^user/(?P<pk>\d+)/$', views.PDFUserDetailView.as_view()),
    url(r'^api/', include(router.urls)),
    url(r'^api/auth', obtain_auth_token),
    url(r'^admin/', admin.site.urls),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^django-rq/', include('django_rq.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
