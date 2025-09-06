
from rest_framework.exceptions import ValidationError
from rest_framework import viewsets, status
from rest_framework.exceptions import NotFound # exception manejada con la respuesta 404
from django.db import IntegrityError 
from .models import Estudiante, Curso, Matricula
from .serializers import EstudianteSerializer, CursoSerializer, MatriculaSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import action #para rutas personalizadas
from rest_framework import filters
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

#opcion1 funcion en vez de vista: http://localhost:8000/api/app/ funcionará.
#@api_view(['GET'])
#def algun_api(request):
 #   return Response({"mensaje": "Hola desde DRF"})

#opcion2 usar DRF routers con la clases. Remplaza las rutas en app y en prueba

class EstudianteViewSet(viewsets.ModelViewSet):
    
    queryset = Estudiante.objects.all()
    serializer_class = EstudianteSerializer

    # Parametros en crear un estudiante  POST
    @swagger_auto_schema(
    operation_description="Crear un nuevo estudiante",
    request_body=EstudianteSerializer,
    responses={
        201: EstudianteSerializer,
        400: "Datos inválidos"
    }
)
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    #customizacion de parametros en update de estudiante  PUT
    @swagger_auto_schema(
    operation_description="Actualizar un estudiante existente",
    request_body=EstudianteSerializer,
    responses={
        200: EstudianteSerializer,
        400: "Datos inválidos",
        404: "Estudiante no encontrado"
    }
)
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    #filtros por termino y orden  en GET
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'email']  # Búsqueda en nombre y email
    ordering_fields = ['nombre', 'email', 'fecha_registro']  # Campos para ordenar
    ordering = ['nombre']  # Orden alfabético por defecto
    # ✅ Documentar MANUALMENTE los parámetros de filtro
    @swagger_auto_schema(  
         manual_parameters=[
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description="Buscar estudiantes por nombre o email. Ej: 'maria', 'maria@email.com'",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'ordering',
                openapi.IN_QUERY,
                description="Ordenar resultados por: nombre, -nombre, email, -email, fecha_registro, -fecha_registro",
                type=openapi.TYPE_STRING,
                required=False
            )
        ],
        operation_description="Lista todos los estudiantes con opciones de búsqueda y ordenamiento"
    )
    def list(self, request, *args, **kwargs):
        """
        Obtiene la lista de estudiantes permitiendo búsqueda por nombre/email 
        y ordenamiento por diferentes campos.
        """
        return super().list(request, *args, **kwargs)
    
    #endpoint adicional  GET estudiante/{id}/cursos para obtener cursos del estudiante
    @swagger_auto_schema(
        operation_description="Obtiene todos los cursos en los que está matriculado un estudiante",
        responses={
            200: openapi.Response(
                description="Lista de cursos del estudiante",
                schema=CursoSerializer(many=True)
            ),
            404: "Estudiante no encontrado"
        }
    )
    @action(detail=True, methods=['get'], url_path='cursos')
    def cursos(self, request, pk=None):
        estudiante = self.get_object()  # obtiene el estudiante con ese ID
        cursos = [matricula.curso for matricula in estudiante.matricula_set.select_related('curso')]
        serializer = CursoSerializer(cursos, many=True)
        return Response(serializer.data)
    
    # custom endpoint para reporte del estudiante
    @swagger_auto_schema(
        operation_description="Genera un reporte académico del estudiante con sus cursos y calificación media",
        responses={
            200: openapi.Response(
                description="Reporte académico del estudiante",
                examples={
                    "application/json": {
                        "nombre": "María García",
                        "detalle": "Este estudiante tiene cursos matriculados.",
                        "cursos": ["Matemáticas", "Física"],
                        "media_calificacion": 8.5,
                        
                    }
                }
            ),
            404: "Estudiante no encontrado"
        }
    )
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

class CursoViewSet(viewsets.ModelViewSet):  #modelviewset proporciona todo el CRUD basico.
    queryset = Curso.objects.all()
    serializer_class = CursoSerializer

    #filtros por termino y ordenamiento
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['activo']  # Aparece como parámetro filter[activo]
    search_fields = ['titulo', 'descripcion']  # Aparece como parámetro search
    ordering_fields = ['titulo', 'fecha_inicio']  # Aparece como parámetro ordering

    # Documentar parámetros de filtro  de GET
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'activo',
                openapi.IN_QUERY,
                description="Filtrar por cursos activos (true) o inactivos (false). Ej: true, false",
                type=openapi.TYPE_BOOLEAN, 
                required=False
            ),
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description="Buscar en título y descripción",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'ordering',
                openapi.IN_QUERY,
                description="Ordenar por: titulo, -titulo, fecha_inicio, -fecha_inicio",
                type=openapi.TYPE_STRING,
                required=False
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """
        Lista todos los cursos con opciones de filtrado, búsqueda y ordenamiento.
        """
        return super().list(request, *args, **kwargs)
    
    # endpoint adicional para obtener estudiantes matriculados en un curso (ID)
    @swagger_auto_schema(
        method='get',
        operation_description="Obtiene todos los estudiantes matriculados en un curso específico",
        operation_summary="Listar estudiantes del curso",
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_PATH,
                description="ID del curso para obtener sus estudiantes",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Lista de estudiantes matriculados en el curso",
                schema=EstudianteSerializer(many=True),
                examples={
                    "application/json": [
                        {
                            "id": 1,
                            "nombre": "María García",
                            "email": "maria@email.com",
                            "fecha_registro": "2023-10-15"
                        },
                        {
                            "id": 2,
                            "nombre": "Juan Pérez",
                            "email": "juan@email.com", 
                            "fecha_registro": "2023-09-20"
                        }
                    ]
                }
            ),
            status.HTTP_404_NOT_FOUND: openapi.Response(
                description="Curso no encontrado",
                examples={
                    "application/json": {
                        "detail": "No se encontró el curso con el ID especificado"
                    }
                }
            )
        }
    )
    @action(detail=True, methods=['get'], url_path='estudiantes')
    def estudiantes(self, request, pk=None):
        curso = self.get_object()  # obtiene el curso con ese ID
        estudiantes = [matricula.estudiante for matricula in curso.matricula_set.select_related('estudiante')] #accede a todas matriculas
        serializado = EstudianteSerializer(estudiantes, many=True) #serializa lista a json
        return Response(serializado.data)

class MatriculaViewSet(viewsets.ModelViewSet):
    queryset = Matricula.objects.all()
    serializer_class = MatriculaSerializer

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['estudiante', 'curso', 'calificacion']
    search_fields = ['estudiante__nombre', 'estudiante__email', 'curso__titulo']
    ordering_fields = ['fecha_matricula', 'calificacion', 'estudiante__nombre', 'curso__titulo']
    ordering = ['-fecha_matricula']  # Más recientes primero

    # doecumentar listado con parametros de search y orden     GET
    @swagger_auto_schema(
        manual_parameters=[
                openapi.Parameter(
                    'estudiante',
                    openapi.IN_QUERY,
                    description="Filtrar por ID de estudiante. Ej: 5",
                    type=openapi.TYPE_INTEGER,
                    required=False
                ),
                openapi.Parameter(
                    'curso',
                    openapi.IN_QUERY,
                    description="Filtrar por ID de curso. Ej: 3",
                    type=openapi.TYPE_INTEGER,
                    required=False
                ),
                openapi.Parameter(
                    'calificacion',
                    openapi.IN_QUERY,
                    description="Filtrar por calificación. Ej: 8.5",
                    type=openapi.TYPE_NUMBER,
                    required=False
                ),
                openapi.Parameter(
                    'calificacion__gte',
                    openapi.IN_QUERY,
                    description="Filtrar por calificación mayor o igual. Ej: 7.0",
                    type=openapi.TYPE_NUMBER,
                    required=False
                ),
                openapi.Parameter(
                    'calificacion__lte',
                    openapi.IN_QUERY,
                    description="Filtrar por calificación menor o igual. Ej: 9.0",
                    type=openapi.TYPE_NUMBER,
                    required=False
                ),
                openapi.Parameter(
                    'search',
                    openapi.IN_QUERY,
                    description="Buscar en nombre/email de estudiante o título de curso. Ej: 'maria', 'matemáticas'",
                    type=openapi.TYPE_STRING,
                    required=False
                ),
                openapi.Parameter(
                    'ordering',
                    openapi.IN_QUERY,
                    description="Ordenar por: fecha_matricula (antiguas primero), -fecha_matricula (recientes primero), calificacion (baja a alta), -calificacion (alta a baja), estudiante__nombre, curso__titulo",
                    type=openapi.TYPE_STRING,
                    required=False
                )
            ],
            operation_description="Lista todas las matrículas con opciones de filtrado, búsqueda y ordenamiento"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    #create matricula
    @swagger_auto_schema(
         operation_description="Crear una nueva matrícula de estudiante en un curso",
        request_body=MatriculaSerializer,
        responses={
            status.HTTP_201_CREATED: MatriculaSerializer,
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description="Datos inválidos o validación fallida",
                examples={
                    "application/json": {
                        "error": {
                            "estudiante": ["Este campo es requerido."],
                            "curso": ["Este campo es requerido."]
                        }
                    }
                }
            ),
            status.HTTP_409_CONFLICT: openapi.Response(
                description="Matrícula duplicada",
                examples={
                    "application/json": {
                        "error": "El estudiante ya está matriculado en este curso."
                    }
                }
            )
        }
    )
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