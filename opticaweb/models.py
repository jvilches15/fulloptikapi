from django.db import models
from django.contrib.auth.models import User

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
    date_of_birth = models.DateField()
    address = models.CharField(max_length=300, blank=True, null=True)
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True)
    comuna = models.ForeignKey(Comuna, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to='perfiles/', null=True, blank=True)

    def __str__(self):
        return self.user.get_full_name()

    
    

# Create your models here.

# Create your models here.
