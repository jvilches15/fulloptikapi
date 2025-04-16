from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rut = models.CharField(max_length=12, unique=True)
    date_of_birth = models.DateField()
    address = models.CharField(max_length=300, blank=True, null=True)
    image = models.ImageField(upload_to='perfiles/', null=True, blank=True)

    def __str__(self):
        return self.user.get_full_name()

# Create your models here.
