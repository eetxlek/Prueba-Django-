from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
# Create your models here.

class Estudiante(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    fecha_registro = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.nombre

class Curso(models.Model):
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    fecha_inicio = models.DateField()
    activo = models.BooleanField(default=False) # al crear se crea inactivo, así que no permite
    #  estudiantes = models.ManyToManyField(Estudiante, related_name='cursos', blank=True)
    # No necesario el campo porque hay una table intermedia Matricula
    # acceso a estudiantes a traves de matriculas : curso.matricula_set.all() o curso.matricula_set.count()
    # tambien... estudiantes = Estudiante.objects.filter(matricula__curso=curso)

    def __str__(self):
        return self.titulo

class Matricula(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    fecha_matricula = models.DateField(auto_now_add=True)
    calificacion = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(10)])
    
    # metodo especial de Django para validaciones personalizadas en los modelos 
    def clean(self):
        # Regla 1: No permitir matrícula en curso inactivo
        # evalúa si el campo activo del curso está en False.
        if not self.curso.activo:
            raise ValidationError("No se puede matricular en un curso inactivo.")

        # Regla 2: No permitir matrícula en curso ya iniciado
        # Compara la fecha de inicio del curso con la fecha actual.
        if self.curso.fecha_inicio < timezone.now().date():
            raise ValidationError("No se puede matricular en un curso que ya comenzó.")

        # Regla 3: Evitar matrícula duplicada (ya cubierta en unique_together)
        # Busca si ya existe una matrícula con el mismo estudiante y curso.
        # si ya hay registro matricula con igual (compara primary key), lanza error
        if Matricula.objects.filter(estudiante=self.estudiante, curso=self.curso).exclude(pk=self.pk).exists():
            raise ValidationError("El estudiante ya está matriculado en este curso.")
        
    #  Sobreescribe el save de modelo para validar datos antes de guardar.    
    def save(self, *args, **kwargs):
        self.clean()  
        super().save(*args, **kwargs)

    # evita que guarden duplicados incluso si se hace una operacion de insert directo con SQL
    class Meta:
        unique_together = ('estudiante', 'curso')

    def __str__(self):
        return f"{self.estudiante.nombre} - {self.curso.titulo}"