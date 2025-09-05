
from rest_framework.exceptions import ValidationError
from rest_framework import viewsets, status
from rest_framework.exceptions import NotFound # exception manejada con la respuestas 404
from django.db import IntegrityError 
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
       
        if not matriculas.exists():
            # esto seria para lanzar un error, pero quiero que devuelva una respuesta 
            #raise NotFound("Este estudiante no tiene cursos matriculados.")  # 404
            
            #RESPUESTA con mensaje, json y status 404
            return Response(
            {
                "nombre": estudiante.nombre,
                "detalle": "Este estudiante no tiene cursos matriculados.",
                "cursos": [],
                "media_calificacion": None
            },
            status=status.HTTP_404_NOT_FOUND
        )
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
    def estudiantes(self, request, pk=None):
        curso = self.get_object()  # obtiene el curso con ese ID
        estudiantes = [matricula.estudiante for matricula in curso.matricula_set.select_related('estudiante')] #accede a todas matriculas
        serializado = EstudianteSerializer(estudiantes, many=True) #serializa lista a json
        return Response(serializado.data)

class MatriculaViewSet(viewsets.ModelViewSet):
    queryset = Matricula.objects.all()
    serializer_class = MatriculaSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)  # excepcion si falla validación o da false  VS el validate lanza un ValidationError
            self.perform_create(serializer) #internamente llama a serializer.save y a model.save.
        
        except ValidationError as e:
            return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError as e:
            # Esto ocurre si se viola unique_together en DB (ej. matrícula duplicada)
            return Response(
                {"error": "El estudiante ya está matriculado en este curso."},
                status=status.HTTP_409_CONFLICT
            )
        return Response(serializer.data, status=status.HTTP_201_CREATED)