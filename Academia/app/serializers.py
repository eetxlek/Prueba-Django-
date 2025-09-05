from django.forms import ValidationError
from rest_framework import serializers
from .models import Estudiante, Curso, Matricula

class EstudianteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estudiante
        fields = '__all__'

class CursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curso
        fields = '__all__'

class MatriculaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Matricula
        fields = '__all__'
        read_only_fields = ['fecha_matricula']  # protege fecha, que no sea modificable con POST o PUT. No se va a incluir en validated_data aunque venga en request.data.
        #ignora el campo matricula si el user lo envia. USA el auto_now_add=True en vez del enviado ha hacer serializer.save.
        # sobreescritura de validate de DRF o hook/gancho que forma parte del ciclo de vida del serializer. Permite validacion personalizada sobre objetos complejos (varios campos a la vez)
        # integra el clean a flujo validacion de DRF
        def validate(self, data):   #drf devuelve un 400 Bad request mediante el def clean.
            # Crear una instancia temporal con los datos recibidos q asegura que se aplique en modelo tambien al validar en DRF serializer.is_valid(campo o objeto) que es llamada automatica.
            instance = Matricula(**data)
            #esta instancia no tiene .pk , django trata como nueva instancia. En clean al  filtrar matricula de un alumno en un curso, puede fallar la actualizacion. Evitar con:
            # conservamos el PK para evitar FALSOS POSITIVOS. pk es necesario para diferenciar crear de actualizar en el clean.
            if self.instance:
                instance.pk = self.instance.pk
            try:
                instance.clean()  # Ejecuta reglas del modelo (como curso inactivo, etc.)
            except ValidationError as e:
                raise serializers.ValidationError(e.message_dict)

            return data
        #validacion de campo individual en vez de todo objeto matricula con el modelo y el clean, solo calificacion a nivel de serializacion.
        #el siguiente solo necesario si haces POST o PUT de madtricula y envias calificacion.     Como en modelo ya esta null=True al crear, no necesario validacion especifica.
        def validate_calificacion(self, value):
            if value < 0 or value > 10:
                raise serializers.ValidationError("Calificación fuera de rango.")
            return value
