from django.contrib import admin
from .models import AdministracionUser
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from .models import Producto
from .models import Venta
from .models import Cita

from django.contrib import admin
from django.contrib.auth.hashers import check_password

class AdministracionUserAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'correo', 'rol', 'rut', 'is_password_set') 
    search_fields = ('nombre', 'correo', 'rol')  
    list_filter = ('rol',)  
    

    def is_password_set(self, obj):
       
        return 'Sí' if obj.password else 'No'  
    
 
    is_password_set.short_description = 'Contraseña configurada'

admin.site.register(AdministracionUser, AdministracionUserAdmin)
admin.site.register(Producto)
admin.site.register(Venta)
admin.site.register(Cita)
