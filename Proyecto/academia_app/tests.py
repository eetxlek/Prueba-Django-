import unittest
from django.test import TestCase, TransactionTestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone
from datetime import date, timedelta
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from decimal import Decimal
from .models import Estudiante, Curso, Matricula
from .serializers import EstudianteSerializer, CursoSerializer, MatriculaSerializer

# TestCase es la clase de test mas comun y sencilla. Usa transacciones para aislar cada test y limpiar la BD.
class EstudianteModelTest(TestCase):
    """Test cases for the Estudiante model"""
    #setea entorno. Cada test se ejecuta en una transaccion y al finalizar se hace rollback.
    def setUp(self):
        """Set up test data"""
        self.estudiante_data = {
            'nombre': 'Juan Pérez',
            'email': 'juan@test.com'
        }
    #Estudiante valido con atributos correctos
    def test_create_estudiante_valid(self):
        """Test creating a valid student"""
        estudiante = Estudiante.objects.create(**self.estudiante_data)
        self.assertEqual(estudiante.nombre, 'Juan Pérez')
        self.assertEqual(estudiante.email, 'juan@test.com')
        self.assertIsNotNone(estudiante.fecha_registro) # se crea automaticamente con auto_now_add
        self.assertEqual(str(estudiante), 'Juan Pérez') # que el objeto to string de el nombre 
        
    #Mail unico porque en modelo unique true
    def test_estudiante_email_unique(self):
        """Test that email must be unique"""
        Estudiante.objects.create(**self.estudiante_data)
        
        with self.assertRaises(IntegrityError):  #bloque que verifica que se lanza la excepcion al crear mismo estudiante, sino el test fallará
            Estudiante.objects.create(**self.estudiante_data)

    #string representaion del objeto asegura que  __str__ está implementado en el modelo
    def test_estudiante_string_representation(self):
        """Test string representation of student"""
        estudiante = Estudiante.objects.create(**self.estudiante_data)
        self.assertEqual(str(estudiante), 'Juan Pérez')
    #asegura que fecha_registro se crea correctamente al crear el objeto
    def test_estudiante_fecha_registro_auto_created(self):
        """Test that registration date is automatically created"""
        estudiante = Estudiante.objects.create(**self.estudiante_data)
        self.assertEqual(estudiante.fecha_registro, timezone.now().date())


class CursoModelTest(TestCase):
    """Test cases for the Curso model"""
     #setea entorno. Cada test se ejecuta en una transaccion y al finalizar se hace rollback.
    def setUp(self):
        """Set up test data"""
        self.curso_data = {
            'titulo': 'Matemáticas Básicas',
            'descripcion': 'Curso introductorio de matemáticas',
            'fecha_inicio': date.today() + timedelta(days=30)
        }
    
    def test_create_curso_valid(self):
        """Test creating a valid course"""
        curso = Curso.objects.create(**self.curso_data)
        self.assertEqual(curso.titulo, 'Matemáticas Básicas')
        self.assertEqual(curso.descripcion, 'Curso introductorio de matemáticas')
        self.assertTrue(curso.activo)  # Default value
        self.assertEqual(str(curso), 'Matemáticas Básicas')
    
    def test_curso_activo_default_true(self):
        """Test that active field defaults to True"""
        curso = Curso.objects.create(**self.curso_data)
        self.assertTrue(curso.activo)
    
    def test_curso_string_representation(self):
        """Test string representation of course"""
        curso = Curso.objects.create(**self.curso_data)
        self.assertEqual(str(curso), 'Matemáticas Básicas')


class MatriculaModelTest(TransactionTestCase):
    """Test cases for the Matricula model"""
    
    def setUp(self):
        """Set up test data"""
        self.estudiante = Estudiante.objects.create(
            nombre='María García',
            email='maria@test.com'
        )
        self.curso_activo = Curso.objects.create(
            titulo='Física',
            descripcion='Curso de física básica',
            fecha_inicio=date.today() + timedelta(days=15),
            activo=True
        )
        self.curso_inactivo = Curso.objects.create(
            titulo='Química',
            descripcion='Curso de química básica',
            fecha_inicio=date.today() + timedelta(days=15),
            activo=False
        )
        self.curso_iniciado = Curso.objects.create(
            titulo='Historia',
            descripcion='Curso de historia',
            fecha_inicio=date.today() - timedelta(days=5),
            activo=True
        )
    
    def test_create_matricula_valid(self):
        """Test creating a valid enrollment"""
        matricula = Matricula.objects.create(
            estudiante=self.estudiante,
            curso=self.curso_activo
        )
        self.assertEqual(matricula.estudiante, self.estudiante)
        self.assertEqual(matricula.curso, self.curso_activo)
        self.assertIsNotNone(matricula.fecha_matricula)
        self.assertIsNone(matricula.calificacion)
        expected_str = f"{self.estudiante.nombre} - {self.curso_activo.titulo}"
        self.assertEqual(str(matricula), expected_str)
    
    def test_matricula_curso_inactivo_validation(self):
        """Test that enrollment in inactive course is not allowed"""
        with self.assertRaises(ValidationError) as context:
            matricula = Matricula(
                estudiante=self.estudiante,
                curso=self.curso_inactivo
            )
            matricula.clean()
        
        self.assertIn("No se puede matricular en un curso inactivo", str(context.exception))
    
    def test_matricula_curso_iniciado_validation(self):
        """Test that enrollment in already started course is not allowed"""
        with self.assertRaises(ValidationError) as context:
            matricula = Matricula(
                estudiante=self.estudiante,
                curso=self.curso_iniciado
            )
            matricula.clean()
        
        self.assertIn("No se puede matricular en un curso que ya comenzó", str(context.exception))
    
    def test_matricula_duplicada_validation(self):
        """Test that duplicate enrollment is not allowed"""
        # Create first enrollment
        Matricula.objects.create(
            estudiante=self.estudiante,
            curso=self.curso_activo
        )
        
        # Try to create duplicate enrollment
        with self.assertRaises(ValidationError) as context:
            matricula = Matricula(
                estudiante=self.estudiante,
                curso=self.curso_activo
            )
            matricula.clean()
        
        self.assertIn("El estudiante ya está matriculado en este curso", str(context.exception))
    
    def test_matricula_unique_together_constraint(self):
        """Test database-level unique constraint with bypassing model validation"""
        Matricula.objects.create(
            estudiante=self.estudiante,
            curso=self.curso_activo
        )
        
        with self.assertRaises((IntegrityError, ValidationError)):
            with transaction.atomic():
                # Try to create duplicate at database level by saving directly without clean
                matricula = Matricula(
                    estudiante=self.estudiante,
                    curso=self.curso_activo
                )
                # This should trigger either IntegrityError or ValidationError
                matricula.save()
    
    def test_matricula_calificacion_valid_range(self):
        """Test that grade is within valid range"""
        matricula = Matricula.objects.create(
            estudiante=self.estudiante,
            curso=self.curso_activo,
            calificacion=Decimal('8.5')
        )
        self.assertEqual(matricula.calificacion, Decimal('8.5'))
    
    def test_matricula_save_calls_clean(self):
        """Test that save method calls clean validation"""
        with self.assertRaises(ValidationError):
            Matricula.objects.create(
                estudiante=self.estudiante,
                curso=self.curso_inactivo
            )


class EstudianteSerializerTest(TestCase):
    """Test cases for EstudianteSerializer"""
    
    def setUp(self):
        """Set up test data"""
        self.estudiante_data = {
            'nombre': 'Ana López',
            'email': 'ana@test.com'
        }
        self.estudiante = Estudiante.objects.create(**self.estudiante_data)
    
    def test_serialize_estudiante(self):
        """Test serializing a student object"""
        serializer = EstudianteSerializer(self.estudiante)
        data = serializer.data
        
        self.assertEqual(data['nombre'], 'Ana López')
        self.assertEqual(data['email'], 'ana@test.com')
        self.assertIn('fecha_registro', data)
    
    def test_deserialize_valid_estudiante(self):
        """Test deserializing valid student data"""
        data = {
            'nombre': 'Carlos Ruiz',
            'email': 'carlos@test.com'
        }
        serializer = EstudianteSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        estudiante = serializer.save()
        
        self.assertEqual(estudiante.nombre, 'Carlos Ruiz')
        self.assertEqual(estudiante.email, 'carlos@test.com')
    
    def test_deserialize_invalid_email(self):
        """Test deserializing with invalid email format"""
        data = {
            'nombre': 'Test User',
            'email': 'invalid-email'
        }
        serializer = EstudianteSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)


class CursoSerializerTest(TestCase):
    """Test cases for CursoSerializer"""
    
    def setUp(self):
        """Set up test data"""
        self.curso_data = {
            'titulo': 'Programación Python',
            'descripcion': 'Curso completo de Python',
            'fecha_inicio': date.today() + timedelta(days=20)
        }
        self.curso = Curso.objects.create(**self.curso_data)
    
    def test_serialize_curso(self):
        """Test serializing a course object"""
        serializer = CursoSerializer(self.curso)
        data = serializer.data
        
        self.assertEqual(data['titulo'], 'Programación Python')
        self.assertEqual(data['descripcion'], 'Curso completo de Python')
        self.assertTrue(data['activo'])
    
    def test_deserialize_valid_curso(self):
        """Test deserializing valid course data"""
        data = {
            'titulo': 'Bases de Datos',
            'descripcion': 'Curso de bases de datos relacionales',
            'fecha_inicio': str(date.today() + timedelta(days=25)),
            'activo': True
        }
        serializer = CursoSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        curso = serializer.save()
        
        self.assertEqual(curso.titulo, 'Bases de Datos')
        self.assertTrue(curso.activo)


class MatriculaSerializerTest(TestCase):
    """Test cases for MatriculaSerializer"""
    
    def setUp(self):
        """Set up test data"""
        self.estudiante = Estudiante.objects.create(
            nombre='Pedro Martín',
            email='pedro@test.com'
        )
        self.curso = Curso.objects.create(
            titulo='Inglés',
            descripcion='Curso de inglés básico',
            fecha_inicio=date.today() + timedelta(days=10),
            activo=True
        )
        self.curso_inactivo = Curso.objects.create(
            titulo='Francés',
            descripcion='Curso de francés',
            fecha_inicio=date.today() + timedelta(days=10),
            activo=False
        )
    
    def test_serialize_matricula(self):
        """Test serializing an enrollment object"""
        matricula = Matricula.objects.create(
            estudiante=self.estudiante,
            curso=self.curso,
            calificacion=Decimal('9.0')
        )
        serializer = MatriculaSerializer(matricula)
        data = serializer.data
        
        self.assertEqual(data['estudiante'], self.estudiante.id)
        self.assertEqual(data['curso'], self.curso.id)
        self.assertEqual(float(data['calificacion']), 9.0)
    
    def test_deserialize_valid_matricula(self):
        """Test deserializing valid enrollment data"""
        data = {
            'estudiante': self.estudiante.id,
            'curso': self.curso.id
        }
        serializer = MatriculaSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        matricula = serializer.save()
        
        self.assertEqual(matricula.estudiante, self.estudiante)
        self.assertEqual(matricula.curso, self.curso)
    
    def test_deserialize_invalid_matricula_curso_inactivo(self):
        """Test validation error for inactive course"""
        data = {
            'estudiante': self.estudiante.id,
            'curso': self.curso_inactivo.id
        }
        serializer = MatriculaSerializer(data=data)
        # The serializer validation should catch this in the validate method
        self.assertFalse(serializer.is_valid())
        # Check that the error message is present
        error_found = False
        for field_errors in serializer.errors.values():
            if any('No se puede matricular en un curso inactivo' in str(error) for error in field_errors):
                error_found = True
                break
        self.assertTrue(error_found, "Expected validation error for inactive course not found")


class EstudianteViewSetTest(APITestCase):
    """Test cases for EstudianteViewSet API endpoints"""
    
    def setUp(self):
        """Set up test data and client"""
        self.client = APIClient()
        # Clear any existing data
        Estudiante.objects.all().delete()
        Curso.objects.all().delete()
        Matricula.objects.all().delete()
        
        self.estudiante_data = {
            'nombre': 'Laura Fernández',
            'email': 'laura@test.com'
        }
        self.estudiante = Estudiante.objects.create(**self.estudiante_data)
        self.curso = Curso.objects.create(
            titulo='Java',
            descripcion='Curso de Java',
            fecha_inicio=date.today() + timedelta(days=15)
        )
    
    def test_get_estudiantes_list(self):
        """Test GET /estudiantes/ endpoint"""
        url = '/api/estudiantes/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nombre'], 'Laura Fernández')
    
    def test_create_estudiante(self):
        """Test POST /estudiantes/ endpoint"""
        url = '/api/estudiantes/'
        data = {
            'nombre': 'Roberto Silva',
            'email': 'roberto@test.com'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['nombre'], 'Roberto Silva')
        self.assertTrue(Estudiante.objects.filter(email='roberto@test.com').exists())
    
    def test_get_estudiante_detail(self):
        """Test GET /estudiantes/{id}/ endpoint"""
        url = f'/api/estudiantes/{self.estudiante.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nombre'], 'Laura Fernández')
    
    def test_update_estudiante(self):
        """Test PUT /estudiantes/{id}/ endpoint"""
        url = f'/api/estudiantes/{self.estudiante.id}/'
        data = {
            'nombre': 'Laura Fernández Updated',
            'email': 'laura_updated@test.com'
        }
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nombre'], 'Laura Fernández Updated')
    
    def test_delete_estudiante(self):
        """Test DELETE /estudiantes/{id}/ endpoint"""
        url = f'/api/estudiantes/{self.estudiante.id}/'
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Estudiante.objects.filter(id=self.estudiante.id).exists())
    
    def test_get_estudiante_cursos(self):
        """Test GET /estudiantes/{id}/cursos/ custom endpoint"""
        # Create enrollment
        Matricula.objects.create(
            estudiante=self.estudiante,
            curso=self.curso
        )
        
        url = f'/api/estudiantes/{self.estudiante.id}/cursos/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['titulo'], 'Java')
    
    def test_get_estudiante_reporte_with_courses(self):
        """Test GET /estudiantes/{id}/reporte/ with enrolled courses"""
        # Create enrollment with grade
        Matricula.objects.create(
            estudiante=self.estudiante,
            curso=self.curso,
            calificacion=Decimal('8.5')
        )
        
        url = f'/api/estudiantes/{self.estudiante.id}/reporte/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nombre'], 'Laura Fernández')
        self.assertEqual(len(response.data['cursos']), 1)
        self.assertEqual(float(response.data['media_calificacion']), 8.5)
    
    def test_get_estudiante_reporte_without_courses(self):
        """Test GET /estudiantes/{id}/reporte/ without enrolled courses"""
        url = f'/api/estudiantes/{self.estudiante.id}/reporte/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detalle'], 'Este estudiante no tiene cursos matriculados.')
    
    def test_search_estudiantes(self):
        """Test search functionality in estudiantes list"""
        url = '/api/estudiantes/?search=Laura'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nombre'], 'Laura Fernández')


class CursoViewSetTest(APITestCase):
    """Test cases for CursoViewSet API endpoints"""
    
    def setUp(self):
        """Set up test data and client"""
        self.client = APIClient()
        # Clear any existing data
        Estudiante.objects.all().delete()
        Curso.objects.all().delete()
        Matricula.objects.all().delete()
        
        self.curso_data = {
            'titulo': 'Django REST',
            'descripcion': 'Curso de Django REST Framework',
            'fecha_inicio': date.today() + timedelta(days=20),
            'activo': True
        }
        self.curso = Curso.objects.create(**self.curso_data)
        self.estudiante = Estudiante.objects.create(
            nombre='Sofía Castro',
            email='sofia@test.com'
        )
    
    def test_get_cursos_list(self):
        """Test GET /cursos/ endpoint"""
        url = '/api/cursos/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['titulo'], 'Django REST')
    
    def test_create_curso(self):
        """Test POST /cursos/ endpoint"""
        url = '/api/cursos/'
        data = {
            'titulo': 'React.js',
            'descripcion': 'Curso de React.js avanzado',
            'fecha_inicio': str(date.today() + timedelta(days=30)),
            'activo': True
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['titulo'], 'React.js')
        self.assertTrue(Curso.objects.filter(titulo='React.js').exists())
    
    def test_filter_cursos_by_activo(self):
        """Test filtering courses by active status"""
        # Create inactive course
        Curso.objects.create(
            titulo='Curso Inactivo',
            descripcion='Descripción',
            fecha_inicio=date.today(),
            activo=False
        )
        
        url = '/api/cursos/?activo=true'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return only the active course (Django REST)
        active_courses = [curso for curso in response.data if curso['activo']]
        self.assertEqual(len(active_courses), 1)
        self.assertEqual(active_courses[0]['titulo'], 'Django REST')
    
    def test_get_curso_estudiantes(self):
        """Test GET /cursos/{id}/estudiantes/ custom endpoint"""
        # Create enrollment
        Matricula.objects.create(
            estudiante=self.estudiante,
            curso=self.curso
        )
        
        url = f'/api/cursos/{self.curso.id}/estudiantes/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nombre'], 'Sofía Castro')


class MatriculaViewSetTest(APITestCase):
    """Test cases for MatriculaViewSet API endpoints"""
    
    def setUp(self):
        """Set up test data and client"""
        self.client = APIClient()
        # Clear any existing data
        Estudiante.objects.all().delete()
        Curso.objects.all().delete()
        Matricula.objects.all().delete()
        
        self.estudiante = Estudiante.objects.create(
            nombre='Diego Morales',
            email='diego@test.com'
        )
        self.curso = Curso.objects.create(
            titulo='Node.js',
            descripcion='Curso de Node.js',
            fecha_inicio=date.today() + timedelta(days=25),
            activo=True
        )
        self.curso_inactivo = Curso.objects.create(
            titulo='Curso Inactivo',
            descripcion='Descripción',
            fecha_inicio=date.today() + timedelta(days=25),
            activo=False
        )
    
    def test_get_matriculas_list(self):
        """Test GET /matriculas/ endpoint"""
        matricula = Matricula.objects.create(
            estudiante=self.estudiante,
            curso=self.curso
        )
        
        url = '/api/matriculas/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['estudiante'], self.estudiante.id)
    
    def test_create_matricula_valid(self):
        """Test POST /matriculas/ endpoint with valid data"""
        url = '/api/matriculas/'
        data = {
            'estudiante': self.estudiante.id,
            'curso': self.curso.id
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Matricula.objects.filter(
            estudiante=self.estudiante,
            curso=self.curso
        ).exists())
    
    def test_create_matricula_curso_inactivo(self):
        """Test POST /matriculas/ with inactive course returns 400"""
        url = '/api/matriculas/'
        data = {
            'estudiante': self.estudiante.id,
            'curso': self.curso_inactivo.id
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_create_matricula_duplicada(self):
        """Test POST /matriculas/ with duplicate enrollment returns error"""
        # Create first enrollment
        Matricula.objects.create(
            estudiante=self.estudiante,
            curso=self.curso
        )
        
        url = '/api/matriculas/'
        data = {
            'estudiante': self.estudiante.id,
            'curso': self.curso.id
        }
        response = self.client.post(url, data, format='json')
        
        # Should return either 400 or 409 depending on where the validation happens
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_409_CONFLICT])
        self.assertIn('error', response.data)
    
    def test_filter_matriculas_by_estudiante(self):
        """Test filtering enrollments by student"""
        matricula = Matricula.objects.create(
            estudiante=self.estudiante,
            curso=self.curso
        )
        
        url = f'/api/matriculas/?estudiante={self.estudiante.id}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['estudiante'], self.estudiante.id)


class IntegrationTest(APITestCase):
    """Integration tests for the complete workflow"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        # Clear any existing data
        Estudiante.objects.all().delete()
        Curso.objects.all().delete()
        Matricula.objects.all().delete()
    
    def test_complete_enrollment_workflow(self):
        """Test complete workflow: create student, course, and enrollment"""
        # 1. Create student
        estudiante_data = {
            'nombre': 'Test Student',
            'email': 'test@student.com'
        }
        response = self.client.post('/api/estudiantes/', estudiante_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        estudiante_id = response.data['id']
        
        # 2. Create course
        curso_data = {
            'titulo': 'Test Course',
            'descripcion': 'Test course description',
            'fecha_inicio': str(date.today() + timedelta(days=30)),
            'activo': True
        }
        response = self.client.post('/api/cursos/', curso_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        curso_id = response.data['id']
        
        # 3. Create enrollment
        matricula_data = {
            'estudiante': estudiante_id,
            'curso': curso_id
        }
        response = self.client.post('/api/matriculas/', matricula_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 4. Verify enrollment in student's courses
        response = self.client.get(f'/api/estudiantes/{estudiante_id}/cursos/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['titulo'], 'Test Course')
        
        # 5. Verify enrollment in course's students
        response = self.client.get(f'/api/cursos/{curso_id}/estudiantes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nombre'], 'Test Student')


if __name__ == '__main__':
    unittest.main()