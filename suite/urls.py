from django.conf.urls import url, include
from django.contrib import admin

from escuelas import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'escuelas', views.EscuelaViewSet)
router.register(r'contactos', views.ContactoViewSet)

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^api/', include(router.urls)),
    url(r'^admin/', admin.site.urls),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
