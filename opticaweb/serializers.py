from rest_framework import serializers
from .models import Consejo

class ConsejoSerializer(serializers.ModelSerializer):
    

    class Meta:
        model = Consejo
        fields = ['id', 'titulo', 'descripcion', 'fecha_publicacion']