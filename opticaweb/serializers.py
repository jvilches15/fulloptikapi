from rest_framework import serializers
from .models import Consejo
from .models import Promocion


class ConsejoSerializer(serializers.ModelSerializer):
    

    class Meta:
        model = Consejo
        fields = ['id', 'titulo', 'descripcion', 'fecha_publicacion']


class PromocionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promocion
        fields = '__all__'