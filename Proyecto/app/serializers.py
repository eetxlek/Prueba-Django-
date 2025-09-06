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
        #ignora el campo matricula si el user lo envia. Usa el auto_now_add=True en vez del enviado ha hacer serializer.save.

        # sobreescritura de validate de DRF o hook/gancho que forma parte del ciclo de vida del serializer. 
        # Permite validacion personalizada sobre objetos (varios campos a la vez)
        # integra el clean al flujo validacion de DRF
        def validate(self, data):   #drf devuelve un 400 Bad request mediante el def clean.
            # Crear una instancia temporal con los datos recibidos en DRF serializer.is_valid(campo o objeto) que llama internamente a este validate.
            instance = Matricula(**data)
            #esta instancia no tiene .pk , django trata como nueva instancia. En clean al filtrar matricula puede fallar actualizacion. 
            # pk es necesario para diferenciar crear de actualizar en el clean. Conservamos antes de pasar al clean. Evita FALSOS POSITIVOS. 
            if self.instance:
                instance.pk = self.instance.pk
            try:
                instance.clean()  # Ejecuta reglas de negocio definidas en el modelo
            except ValidationError as e:
                raise serializers.ValidationError(e.message_dict)  # Error se atrapa dentro de DRF y view devuelve 400 con detalles

            return data
      
