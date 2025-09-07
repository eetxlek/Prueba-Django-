from django.db import migrations
from datetime import date, timedelta

def insert_initial_data(apps, schema_editor):
    # Obtener modelos desde apps (no directamente importados)
    Estudiante = apps.get_model('academia_app', 'Estudiante')
    Curso = apps.get_model('academia_app', 'Curso')
    Matricula = apps.get_model('academia_app', 'Matricula')

    # Crear estudiantes iniciales
    estudiantes = [
        Estudiante(nombre="Juan Pérez", email="juan.perez@email.com"),
        Estudiante(nombre="Lucía Gómez", email="lucia.gomez@email.com"),
        Estudiante(nombre="Pedro Torres", email="pedro.torres@email.com"),
        Estudiante(nombre="Ana Ruiz", email="ana.ruiz@email.com"),
        Estudiante(nombre="Miguel Herrera", email="miguel.herrera@email.com"),
    ]
    Estudiante.objects.bulk_create(estudiantes)

    # Crear cursos iniciales (algunos activos, otros no)
    hoy = date.today()
    cursos = [
        Curso(
            titulo="Matemáticas Básicas",
            descripcion="Curso introductorio a las matemáticas.",
            fecha_inicio=hoy + timedelta(days=10),
            activo=True
        ),
        Curso(
            titulo="Historia Universal",
            descripcion="Curso sobre los eventos históricos más importantes.",
            fecha_inicio=hoy + timedelta(days=5),
            activo=True
        ),
        Curso(
            titulo="Física Moderna",
            descripcion="Relatividad, mecánica cuántica y más.",
            fecha_inicio=hoy + timedelta(days=20),
            activo=False
        ),
        Curso(
            titulo="Programación en Python",
            descripcion="Curso de introducción a la programación con Python.",
            fecha_inicio=hoy + timedelta(days=15),
            activo=True
        )
    ]
    Curso.objects.bulk_create(cursos)

    # Obtener instancias ya guardadas
    estudiantes = list(Estudiante.objects.all())
    cursos = list(Curso.objects.filter(activo=True))

    # Crear algunas matrículas válidas
    matriculas = [
        Matricula(estudiante=estudiantes[0], curso=cursos[0], calificacion=8.5),
        Matricula(estudiante=estudiantes[1], curso=cursos[0], calificacion=7.0),
        Matricula(estudiante=estudiantes[2], curso=cursos[1], calificacion=9.0),
        Matricula(estudiante=estudiantes[3], curso=cursos[2], calificacion=None),  # Este curso está inactivo, ¡verifica tus validaciones!
        Matricula(estudiante=estudiantes[4], curso=cursos[1], calificacion=6.8),
    ]
    # Solo matriculamos en cursos activos y futuros para cumplir validaciones
    Matricula.objects.bulk_create([m for m in matriculas if m.curso.activo and m.curso.fecha_inicio >= hoy])

def reverse_initial_data(apps, schema_editor):
    Estudiante = apps.get_model('academia_app', 'Estudiante')
    Curso = apps.get_model('academia_app', 'Curso')
    Matricula = apps.get_model('academia_app', 'Matricula')

    # Borrar en orden inverso por integridad referencial
    Matricula.objects.all().delete()
    Curso.objects.all().delete()
    Estudiante.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
       ('academia_app', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(insert_initial_data),
    ]
