from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Estudiante
from .models import Curso
from .models import Matricula   

admin.site.register(Estudiante)
admin.site.register(Curso)
admin.site.register(Matricula)