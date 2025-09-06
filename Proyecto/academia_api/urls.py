"""
URL configuration for Academia project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.routers import DefaultRouter
from app.views import EstudianteViewSet, CursoViewSet, MatriculaViewSet

# para asociar vista a /api  aunque aun te faltaria asociar vistas tambien para esas urls, que no lo veo mucho sentido ahora mismo.
router = DefaultRouter()
router.register(r'estudiantes', EstudianteViewSet)
router.register(r'cursos', CursoViewSet)
router.register(r'matriculas', MatriculaViewSet)

# Configuración de Swagger
schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation",
        default_version='v1',
        description="Documentación de la API",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls), # Panel de administración de Django, si usas admin
    path('api/', include(router.urls)), # Mis endpoints del API
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'), # Documentacion interactiva Swagger
     #path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'), # Devuelve el esquema en JSON o YAML,   NO NECESARIO, para generar clientes y validaciones automaticas
]
