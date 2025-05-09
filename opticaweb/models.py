from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.utils import timezone




class Region(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nombre

class Comuna(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='comunas')

    def __str__(self):
        return self.nombre

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rut = models.CharField(max_length=12, unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=300, blank=True, null=True)
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True)
    comuna = models.ForeignKey(Comuna, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to='perfiles/', null=True, blank=True)

    def __str__(self):
        return self.user.get_full_name()

class AdministracionUser(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.SET_NULL)
    rut = models.CharField(max_length=12, unique=True)
    nombre = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    password = models.CharField(max_length=255)  

    ROL_CHOICES = [
        ('administrador', 'Administrador'),
        ('colaborador', 'Colaborador')
    ]
    rol = models.CharField(max_length=20, choices=ROL_CHOICES)

    def __str__(self):
        return f"{self.nombre} ({self.rol})"
    
   
    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save()

   
    def check_password(self, raw_password):
        from django.contrib.auth.hashers import check_password
        return check_password(raw_password, self.password)
    
    
class Producto(models.Model):
     nombre = models.CharField(max_length=100)
     descripcion = models.TextField(blank=True)
     precio = models.DecimalField(max_digits=10, decimal_places=2)
     stock = models.PositiveIntegerField()
     imagen = models.ImageField(upload_to='productos/', null=True, blank=True)

def __str__(self):
        return self.nombre

class Venta(models.Model):
    usuario = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)  
    cantidad = models.PositiveIntegerField()
    monto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
       
        from .models import Producto  
        
        if self.producto:
            self.monto = self.producto.precio * self.cantidad
        super(Venta, self).save(*args, **kwargs)
        
class Cita(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('rechazada', 'Rechazada'),
    ]
    
    usuario = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='citas')
    fecha = models.DateTimeField()
    motivo = models.TextField()
    estado = models.CharField(max_length=10, choices=ESTADOS, default='pendiente')

    def __str__(self):
        return f"{self.usuario.user.get_full_name()} - {self.fecha.strftime('%d/%m/%Y %H:%M')}"

    def get_estado_display(self):
        return dict(self.ESTADOS).get(self.estado, 'Pendiente')
    
class Consejo(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha_publicacion = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.titulo
    
class Promocion(models.Model):
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    activa = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.titulo} ({'Activa' if self.activa else 'Inactiva'})"

  


# Create your models here.


