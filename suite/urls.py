from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.static import static

from escuelas import views
from rest_framework import routers

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'users', views.UserViewSet)
router.register(r'escuelas', views.EscuelaViewSet)
router.register(r'contactos', views.ContactoViewSet)
router.register(r'eventos', views.EventoViewSet)
router.register(r'regiones', views.RegionViewSet)
router.register(r'perfiles', views.PerfilViewSet)

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^api/', include(router.urls)),
    url(r'^admin/', admin.site.urls),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
