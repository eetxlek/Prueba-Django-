# Academia API

API RESTful para la gestión de estudiantes, cursos y matrículas. Desarrollada con **Django** y **Django REST Framework**, con validaciones personalizadas y documentación interactiva vía Swagger.

---

## ¿Qué incluye este proyecto?

Este proyecto se entrega como un archivo `.zip` con la siguiente estructura:

Proyecto/
│
├── academia_api/ # Configuración principal del proyecto Django
├── academia_app/ # Aplicación con modelos, vistas y serializadores
├── db.sqlite3 # Base de datos preconfigurada (opcional)
├── manage.py # Script de gestión de Django
├── requirements.txt # Dependencias del proyecto
└── README.md # Esta guía de instalación

## Pasos para ejecutar la aplicación

### 1. Descomprimir el ZIP

Descomprime el archivo `Prueba_tecnica_academia.zip` en tu escritorio o en una carpeta de tu preferencia: 

---

### 2. Crear un entorno virtual (recomendado)

```bash
# Dentro de la carpeta del proyecto:
cd Proyecto

# Crear entorno virtual
python -m venv venv

# Activarlo
venv\Scripts\activate   # En Windows
# source venv/bin/activate   # En Linux o MacOS
```
### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Aplicar migraciones

```bash
#Esto creará la base de datos, el fichero db.sqlite3, si no existe.
python manage.py migrate
```

### 5. Ejecutar el servidor de desarrollo

```bash
python manage.py runserver
```

## Documentacion Swagger

Documentación interactiva de la API:

http://127.0.0.1:8000
http://127.0.0.1:8000/swagger/

## Ejecutar pruebas

Puedes lanzar los test con:

```bash
python manage.py test
```

## Funcionalidades

CRUD completo para:

- Estudiantes
- Cursos
- Matrículas

Validaciones de negocio:

- No se permite matricular en cursos inactivos
- No se permite matricular en cursos ya iniciados
- No se permite duplicar matrículas de un estudiante en el mismo curso

Campos protegidos:

- fecha_matricula no es editable por el usuario

Endpoints adicionales:

- GET /estudiantes/{id}/cursos/ — Cursos de un estudiante
- GET /estudiantes/{id}/reporte/ — Reporte académico con promedio
- GET /cursos/{id}/estudiantes/ — Estudiantes de un curso

Filtros disponibles en todos los endpoints:

- Búsqueda (search)
- Ordenamiento (ordering)
- Filtros por campos (filter)

Documentación Swagger generada automáticamente con DRF y drf-yasg

## Dependencias principales

- Django – Framework principal para backend
- djangorestframework – Para crear APIs REST
- drf-yasg – Generación automática de documentación Swagger/OpenAPI
- django-cors-headers – Para permitir peticiones CORS desde el frontend (React, etc.)