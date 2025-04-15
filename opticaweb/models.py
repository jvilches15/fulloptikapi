from django.db import models

class UserProfile(models.Model):
    full_name = models.CharField(max_length=200)
    rut = models.CharField(max_length=12, unique=True)  
    email = models.EmailField()
    date_of_birth = models.DateField()
    address = models.CharField(max_length=300, blank=True, null=True)  

    def __str__(self):
        return self.full_name
# Create your models here.
