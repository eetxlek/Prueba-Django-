from django.shortcuts import render

# Create your views here.

from rest_framework import viewsets
from .models import Estudiante, Curso, Matricula
from .serializers import EstudianteSerializer, CursoSerializer, MatriculaSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import action #para rutas personalizadas

#opcion1 funcion en vez de vista: http://localhost:8000/api/app/ funcionará.
#@api_view(['GET'])
#def algun_api(request):
 #   return Response({"mensaje": "Hola desde DRF"})

#opcion2 usar DRF routers con la clases. Remplaza las rutas en app y en prueba

class EstudianteViewSet(viewsets.ModelViewSet):
    queryset = Estudiante.objects.all()
    serializer_class = EstudianteSerializer

    #endpoint adicional
    @action(detail=True, methods=['get'], url_path='cursos')
    def cursos(self, request, pk=None):
        estudiante = self.get_object()  # obtiene el estudiante con ese ID
        cursos = [matricula.curso for matricula in estudiante.matricula_set.select_related('curso')]
        serializer = CursoSerializer(cursos, many=True)
        return Response(serializer.data)
    
    # custom endpoint para reporte del estudiante
    @action(detail=True, methods=['get'], url_path='reporte')
    def reporte(self, request, pk=None):
        estudiante = self.get_object()

        # Obtener todos los cursos en los que está matriculado
        matriculas = estudiante.matricula_set.select_related('curso')

        cursos = [m.curso.titulo for m in matriculas]

        # Calcular promedio solo si hay calificaciones no nulas
        calificaciones = [m.calificacion for m in matriculas if m.calificacion is not None]
        media = sum(calificaciones) / len(calificaciones) if calificaciones else None

        data = {
            "nombre": estudiante.nombre,
            "cursos": cursos,
            "media_calificacion": round(media, 2) if media is not None else None
        }

        return Response(data)

class CursoViewSet(viewsets.ModelViewSet):
    queryset = Curso.objects.all()
    serializer_class = CursoSerializer

    @action(detail=True, methods=['get'], url_path='estudiantes')
    def estudiante(self, request, pk=None):
        curso = self.get_object()  # obtiene el curso con ese ID
        estudiantes = [matricula.estudiante for matricula in curso.matricula_set.select_related('estudiante')] #accede a todas matriculas
        serializer = EstudianteSerializer(estudiantes, many=True) #serializa lista a json
        return Response(serializer.data)

class MatriculaViewSet(viewsets.ModelViewSet):
    queryset = Matricula.objects.all()
    serializer_class = MatriculaSerializer