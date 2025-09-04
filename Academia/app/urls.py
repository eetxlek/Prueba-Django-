#from django.urls import path
#from . import views

 #opcion2 -> DRF router con clases. Genera los endpoints automaticamente, consulta en http://localhost:8000/swagger/
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EstudianteViewSet, CursoViewSet, MatriculaViewSet

router = DefaultRouter()
router.register(r'estudiante', EstudianteViewSet)
router.register(r'curso', CursoViewSet)
router.register(r'matricula', MatriculaViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

#rutas especificas de la app

#opcion1
#urlpatterns = [ path('app/', views.algun_api, name='api'),]
   
